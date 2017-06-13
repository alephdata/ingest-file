import logging
import mimetypes
from ingestors.util import normalize_mime_type, normalize_extension

log = logging.getLogger(__name__)


class Ingestor(object):
    """Generic ingestor class."""
    MIME_TYPES = []
    EXTENSIONS = []
    SCORE = 3

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
        if mime_type is None:
            (mime_type, enc) = mimetypes.guess_type(file_path)

        if mime_type is not None:
            for match_type in cls.MIME_TYPES:
                match_type = normalize_mime_type(match_type)
                if normalize_mime_type is None:
                    continue
                if match_type.lower().strip() == mime_type.lower().strip():
                    return cls.SCORE

        extensions = [normalize_extension(e) for e in cls.EXTENSIONS]
        extensions = [e for e in extensions if e is not None]
        if normalize_extension(file_path) in extensions:
            return cls.SCORE

        return -1
