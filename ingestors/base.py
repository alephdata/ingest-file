import os
import logging
import mimetypes
from ingestors.util import normalize_mime_type

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

        path, ext = os.path.splitext(file_path)
        ext = ext.strip('.').strip().lower()
        if ext in [e.lower().strip() for e in cls.EXTENSIONS]:
            return cls.SCORE

        return -1
