import os
import magic
import logging
import time
from pkg_resources import iter_entry_points

from followthemoney import model
from servicelayer.archive import init_archive
from balkhash import init

from ingestors.directory import DirectoryIngestor
from ingestors.exc import ProcessingException, SystemException
from ingestors.util import is_file, safe_string
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
    INGESTORS = []

    def __init__(self, dataset, context):
        self.archive = init_archive()
        # TODO: Probably a good idea to make context readonly since we are
        # reusing it in child ingestors
        self.dataset = dataset
        self.context = context
        self.key_prefix = dataset

    @classmethod
    def ingestors(cls):
        if not len(cls.INGESTORS):
            for ep in iter_entry_points('ingestors'):
                cls.INGESTORS.append(ep.load())
        return cls.INGESTORS

    def make_entity(self, schema):
        schema = model.get(schema)
        return model.make_entity(schema, key_prefix=self.key_prefix)

    def emit_entity(self, entity):
        from pprint import pprint
        pprint(entity.to_dict())
        # self.entities.append(entity)

    def auction(self, file_path, entity):
        if not is_file(file_path):
            entity.add('mimeType', DirectoryIngestor.MIME_TYPE)
            return DirectoryIngestor

        if not entity.has('mimeType'):
            entity.add('mimeType', self.MAGIC.from_file(file_path))

        best_score, best_cls = 0, None
        for cls in self.__class__.ingestors():
            score = cls.match(file_path, entity)
            if score > best_score:
                best_score = score
                best_cls = cls

        if best_cls is None:
            raise ProcessingException("Format not supported")
        return best_cls

    def handle_child(self, file_path, child):
        if is_file(file_path):
            checksum = self.archive.archive_file(file_path)
            child.set('contentHash', checksum)
            child.set('fileSize', os.path.getsize(file_path))
        self.ingest(file_path, child)

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
            return self.emit_entity(entity)

    def delegate(self, ingestor_class, file_path, entity):
        ingestor = ingestor_class(self)
        try:
            ingestor.ingest(file_path, entity)
        finally:
            ingestor.cleanup()

    def get_filepath(self, entity):
        return self.archive.load_file(entity.first('contentHash'))

    def get_dataset(self):
        return init(self.dataset, backend=settings.BALKHASH_BACKEND_ENV)

    def balkhash_emit(self, entity, fragment=None):
        writer = self.get_dataset()
        log.debug("Store entity [%(schema)s]: %(id)s", entity)
        writer.put(entity, fragment)
        writer.close()
