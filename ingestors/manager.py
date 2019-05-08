import os
import time
import magic
import logging
import balkhash
from tempfile import mkdtemp
from followthemoney import model
from servicelayer.archive import init_archive
from servicelayer.extensions import get_extensions

from ingestors.directory import DirectoryIngestor
from ingestors.exc import ProcessingException, SystemException
from ingestors.util import is_directory, is_file, safe_string
from ingestors.util import remove_directory
from ingestors import settings

log = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 5
RETRY_BACKOFF_FACTOR = 2


class Manager(object):
    """Handles the lifecycle of an ingestor. This can be subclassed to embed it
    into a larger processing framework."""

    STATUS_PENDING = u'pending'
    #: Indicates that during the processing no errors or failures occured.
    STATUS_SUCCESS = u'success'
    #: Indicates occurance of errors during the processing.
    STATUS_FAILURE = u'failure'
    #: Indicates a complete ingestor stop due to system issue.
    STATUS_STOPPED = u'stopped'

    MAGIC = magic.Magic(mime=True)

    def __init__(self, queue, context):
        self.queue = queue
        # TODO: Probably a good idea to make context readonly since we are
        # reusing it in child ingestors
        self.context = context
        self.work_path = mkdtemp(prefix='ingestor-')
        self._emit_count = 0

    @property
    def archive(self):
        if not hasattr(settings, '_archive'):
            settings._archive = init_archive()
        return settings._archive

    def get_dataset(self):
        return balkhash.init(self.queue.dataset)

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
        # writer = self.get_dataset()
        # writer.put(entity, fragment)
        # writer.close()
        self._emit_count += 1

    def emit_text_fragment(self, entity, text, fragment):
        doc = self.make_entity(entity.schema)
        doc.id = entity.id
        doc.add('indexText', text)
        self.emit_entity(doc, fragment=str(fragment))

    def get_filepath(self, entity):
        return self.archive.load_file(entity.first('contentHash'),
                                      temp_path=self.work_path)

    def auction(self, file_path, entity):
        if is_directory(file_path):
            entity.add('mimeType', DirectoryIngestor.MIME_TYPE)
            return DirectoryIngestor

        if not entity.has('mimeType'):
            entity.add('mimeType', self.MAGIC.from_file(file_path))

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

    def archive_entity(self, entity, file_path):
        if is_file(file_path):
            checksum = self.archive.archive_file(file_path)
            entity.set('contentHash', checksum)
            entity.set('fileSize', os.path.getsize(file_path))
            return checksum

    def handle_child(self, file_path, child):
        self.archive_entity(child, file_path)
        file_name = os.path.basename(file_path)
        child.add('fileName', file_name)
        self.queue_entity(child)

    def ingest(self, file_path, entity, **kwargs):
        """Main execution step of an ingestor."""
        try:
            ingestor_class = self.auction(file_path, entity)
            log.info("Ingestor [%r]: %s", entity, ingestor_class.__name__)
            self.delegate(ingestor_class, file_path, entity)
            entity.set('processingStatus', self.STATUS_SUCCESS)
        except SystemException as pexc:
            retries = kwargs.get('retries', 0)
            backoff = kwargs.get('backoff', RETRY_BACKOFF_SECONDS)
            if retries < MAX_RETRIES:
                time.sleep(backoff)
                retries = retries + 1
                backoff = backoff * RETRY_BACKOFF_FACTOR
                self.ingest(
                    file_path, entity, retries=retries, backoff=backoff
                )
                return
            entity.set('processingStatus', self.STATUS_STOPPED)
            entity.set('processingError', safe_string(pexc))
            log.warning("Stopped [%r]: %s", entity, pexc)
        except (ProcessingException, Exception) as pexc:
            entity.set('processingStatus', self.STATUS_FAILURE)
            entity.set('processingError', safe_string(pexc))
            log.warning("Failed [%r]: %s", entity, pexc)
        finally:
            self.emit_entity(entity)
            self.finalize()

    def delegate(self, ingestor_class, file_path, entity):
        ingestor = ingestor_class(self)
        ingestor.ingest(file_path, entity)

    def finalize(self):
        log.debug("Emitted %d entities", self._emit_count)
        status = self.queue.progress.get()
        if status.get('pending') == 0:
            log.debug('DONE: %s', self.queue.dataset)
        remove_directory(self.work_path)
