import magic
import logging
from pathlib import Path
from tempfile import mkdtemp

import balkhash
from followthemoney import model
from servicelayer.archive import init_archive
from servicelayer.extensions import get_extensions

from ingestors.directory import DirectoryIngestor
from ingestors.exc import ProcessingException
from ingestors.util import safe_string
from ingestors.util import remove_directory
from ingestors import settings

log = logging.getLogger(__name__)


class Manager(object):
    """Handles the lifecycle of an ingestor. This can be subclassed to embed it
    into a larger processing framework."""

    #: Indicates that during the processing no errors or failures occured.
    STATUS_SUCCESS = u'success'
    #: Indicates occurance of errors during the processing.
    STATUS_FAILURE = u'failure'

    MAGIC = magic.Magic(mime=True)

    def __init__(self, queue, context):
        self.queue = queue
        # TODO: Probably a good idea to make context readonly since we are
        # reusing it in child ingestors
        self.context = context
        self.work_path = Path(mkdtemp(prefix='ingestor-'))
        self._emit_count = 0
        self._writer = None
        self._dataset = None

    @property
    def archive(self):
        if not hasattr(settings, '_archive'):
            settings._archive = init_archive()
        return settings._archive

    @property
    def dataset(self):
        if self._dataset is None:
            self._dataset = balkhash.init(self.queue.dataset)
        return self._dataset

    @property
    def writer(self):
        if self._writer is None:
            self._writer = self.dataset.bulk()
        return self._writer

    def make_entity(self, schema, parent=None):
        schema = model.get(schema)
        entity = model.make_entity(schema, key_prefix=self.queue.dataset)
        self.make_child(parent, entity)
        return entity

    def make_child(self, parent, child):
        if parent is not None and child is not None:
            child.add('parent', parent.id)
            child.add('ancestors', parent.get('ancestors'))
            child.add('ancestors', parent.id)

    def emit_entity(self, entity, fragment=None):
        # from pprint import pprint
        # pprint(entity.to_dict())
        self.writer.put(entity.to_dict(), fragment)
        self._emit_count += 1

    def emit_text_fragment(self, entity, text, fragment):
        doc = self.make_entity(entity.schema)
        doc.id = entity.id
        doc.add('indexText', text)
        self.emit_entity(doc, fragment=str(fragment))

    def auction(self, file_path, entity):
        if not entity.has('mimeType'):
            if file_path.is_dir():
                entity.add('mimeType', DirectoryIngestor.MIME_TYPE)
                return DirectoryIngestor
            entity.add('mimeType', self.MAGIC.from_file(file_path.as_posix()))

        best_score, best_cls = 0, None
        for cls in get_extensions('ingestors'):
            score = cls.match(file_path, entity)
            if score > best_score:
                best_score = score
                best_cls = cls

        if best_cls is None:
            raise ProcessingException("Format not supported")
        return best_cls

    def queue_entity(self, entity):
        log.debug("Queue: %r", entity)
        self.queue.queue_task(entity.to_dict(), self.context)

    def archive_store(self, file_path):
        if file_path.is_file():
            return self.archive.archive_file(file_path)

    def ingest_entity(self, entity):
        for content_hash in entity.get('contentHash'):
            file_path = self.archive.load_file(content_hash,
                                               temp_path=self.work_path)
            if file_path is None:
                continue
            file_path = Path(file_path).resolve()
            if not file_path.exists():
                continue
            self.ingest(file_path, entity)
            return
        self.finalize(entity)

    def ingest(self, file_path, entity, **kwargs):
        """Main execution step of an ingestor."""
        file_path = Path(file_path).resolve()
        if file_path.is_file() and not entity.has('fileSize'):
            entity.add('fileSize', file_path.stat().st_size)

        try:
            ingestor_class = self.auction(file_path, entity)
            log.info("Ingestor [%r]: %s", entity, ingestor_class.__name__)
            self.delegate(ingestor_class, file_path, entity)
            entity.set('processingStatus', self.STATUS_SUCCESS)
        except ProcessingException as pexc:
            entity.set('processingStatus', self.STATUS_FAILURE)
            entity.set('processingError', safe_string(pexc))
            log.exception("Failed to process: %r", entity)
        finally:
            self.finalize(entity)

    def finalize(self, entity):
        self.emit_entity(entity)
        self.writer.flush()
        log.debug("Emitted %d entities", self._emit_count)
        self._emit_count = 0

    def delegate(self, ingestor_class, file_path, entity):
        ingestor_class(self).ingest(file_path, entity)

    def close(self):
        self.writer.flush()
        self.dataset.close()
        remove_directory(self.work_path)
