import six
import logging
from pkg_resources import iter_entry_points

import magic

from ingestors.exc import ProcessingException

log = logging.getLogger(__name__)


class IngestorResult(object):

    #: Indicates that during the processing no errors or failures occured.
    STATUS_SUCCESS = u'success'
    #: Indicates occurance of errors during the processing.
    STATUS_FAILURE = u'failure'
    #: Indicates a complete ingestor stop due to system issue.
    STATUS_STOPPED = u'stopped'

    def __init__(self, file_path=None, mime_type=None):
        self.status = None
        self.file_path = file_path
        self.mime_type = mime_type
        self.error_message = None

    def create_child(self, file_path):
        pass

    def to_dict(self):
        return {
            'status': self.status,
            'file_path': self.file_path,
            'mime_type': self.mime_type,
            'error_message': self.error_message
        }


class IngestorManager(object):
    """Handles the lifecycle of an ingestor. This can be subclassed to embed it
    into a larger processing framework."""

    RESULT_CLASS = IngestorResult
    MAGIC = magic.Magic(mime=True)

    def __init__(self, config):
        self.config = config

    @property
    def ingestors(self):
        if not hasattr(self, '_ingestors'):
            self._ingestors = []
            for ep in iter_entry_points('ingestors'):
                self._ingestors.append(ep.load())
        return self._ingestors

    def auction(self, file_path, result):
        if result.mime_type is None:
            result.mime_type = self.MAGIC.from_file(file_path)

        best_score, best_cls = 0, None
        for cls in self.ingestors:
            score = cls.match(file_path, mime_type=result.mime_type)
            if score > best_score:
                best_score = score
                best_cls = cls

        if best_cls is None:
            raise ProcessingException("Format not supported: %r (%s)" %
                                      (file_path, result.mime_type))
        return best_cls

    def before(self, result):
        """Callback called before the processing starts."""
        pass

    def after(self, result):
        """Callback called after the processing starts."""
        pass

    def handle_child(self, result, file_path):
        # check if it's a directory, otherwise archive straight away
        pass

    def execute(self, file_path, result=None, ingestor_class=None):
        """Main execution step of an ingestor."""
        if result is None:
            result = self.RESULT_CLASS(file_path=file_path)

        self.before(result)
        try:
            if ingestor_class is None:
                ingestor_class = self.auction(file_path, result)
                log.debug("Ingestor [%s, %s]: %r", file_path, result.mime_type,
                          ingestor_class)
            ingestor = ingestor_class(self, result)
            ingestor.ingest(file_path)
            result.status = IngestorResult.STATUS_SUCCESS
        except ProcessingException as pexc:
            result.error_message = six.text_type(pexc)
            result.status = IngestorResult.STATUS_FAILURE
        except Exception as exception:
            log.exception(exception)
            result.status = IngestorResult.STATUS_STOPPED
        finally:
            self.after(result)

        return result


class Ingestor(object):
    """Generic ingestor class."""
    MIME_TYPES = []

    def __init__(self, manager, result):
        self.manager = manager
        self.result = result

    def ingest(self, file_path):
        """The ingestor implementation. Should be overwritten.

        This method does not return anything.
        Use the ``result`` attribute to store any resulted data.
        """
        raise NotImplemented()

    @classmethod
    def match(cls, file_path, mime_type=None):
        if mime_type is not None:
            for match_type in cls.MIME_TYPES:
                if match_type.lower().strip() == mime_type.lower().strip():
                    return 2
        return -1
