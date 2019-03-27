import os
import magic
import logging
import hashlib
from servicelayer.archive import init_archive
from pantomime import normalize_mimetype, useful_mimetype
from normality import stringify
from followthemoney import model
# from followthemoney.types import registry
from servicelayer.archive import init_archive
from pantomime import normalize_mimetype, useful_mimetype
from pkg_resources import iter_entry_points

from ingestors.directory import DirectoryIngestor
from ingestors.exc import ProcessingException
from ingestors.util import is_file, safe_string

log = logging.getLogger(__name__)


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

    def __init__(self, archive=None, key_prefix=None):
        self.key_prefix = key_prefix
        self.archive = archive or init_archive()
        self.entities = []

    @property
    def ingestors(self):
        if not len(self.INGESTORS):
            for ep in iter_entry_points('ingestors'):
                self.INGESTORS.append(ep.load())
        return self.INGESTORS

    
    def make_entity(self, schema):
        schema = model.get(schema)
        return model.make_entity(schema, key_prefix=self.key_prefix)

    def emit_entity(self, entity):
        from pprint import pprint
        pprint(entity.to_dict())
        self.entities.append(entity)
        pass

    def auction(self, file_path, entity):
        if not is_file(file_path):
            entity.add('mimeType', DirectoryIngestor.MIME_TYPE)
            return DirectoryIngestor

        if not entity.has('mimeType'):
            entity.add('mimeType', self.MAGIC.from_file(file_path))

        best_score, best_cls = 0, None
        for cls in self.ingestors:
            score = cls.match(file_path, entity)
            if score > best_score:
                best_score = score
                best_cls = cls

        if best_cls is None:
            raise ProcessingException("Format not supported")
        return best_cls

    def handle_child(self, file_path, child):
        self.ingest(file_path, child)

    def checksum_file(self, entity, file_path):
        "Generate a hash and file size for a given file name."
        if not is_file(file_path):
            return

        if not entity.has('contentHash'):
            checksum = hashlib.sha1()
            size = 0
            with open(file_path, 'rb') as fh:
                while True:
                    block = fh.read(8192)
                    if not block:
                        break
                    size += len(block)
                    checksum.update(block)

            entity.set('contentHash', checksum.hexdigest())
            entity.set('fileSize', size)

        if not entity.has('fileSize'):
            entity.add('fileSize', os.path.getsize(file_path))

    def ingest(self, file_path, entity=None, work_path=None):
        """Main execution step of an ingestor."""
        if entity is None:
            entity = self.make_entity('Document')
            file_name = os.path.basename(file_path) if file_path else None
            entity.set('fileName', file_name)

        self.checksum_file(entity, file_path)
        # entity.set('processingStatus', self.STATUS_PENDING)
        try:
            ingestor_class = self.auction(file_path, entity)
            log.info("Ingestor [%r]: %s", entity, ingestor_class.__name__)
            self.delegate(ingestor_class, file_path, entity,
                          work_path=work_path)
            # entity.set('processingStatus', self.STATUS_SUCCESS)
        except ProcessingException as pexc:
            # entity.set('processingStatus', self.STATUS_FAILURE)
            # entity.set('processingError', safe_string(pexc))
            log.warning("Failed [%r]: %s", entity, pexc)
        finally:
            pass
            # if self.STATUS_PENDING in entity.get('processingStatus'):
                # entity.set('processingStatus', self.STATUS_SUCCESS)

        self.emit_entity(entity)

    def delegate(self, ingestor_class, file_path, entity, work_path=None):
        ingestor = ingestor_class(self, work_path=work_path)
        try:
            ingestor.ingest(file_path, entity)
        finally:
            ingestor.cleanup()
