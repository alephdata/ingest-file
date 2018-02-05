import logging
from datetime import date, datetime
from celestial import normalize_mimetype
from ingestors.util import normalize_extension
from ingestors.util import safe_string

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

    def update(self, name, value):
        """Set a metadata value if it is not already set with a value."""
        existing = getattr(self.result, name)
        if existing:
            return
        if not isinstance(value, (date, datetime)):
            value = safe_string(value)
        if value is None:
            return
        setattr(self.result, name, value)

    @classmethod
    def match(cls, file_path, result=None):
        mime_type = normalize_mimetype(result.mime_type, default=None)
        if mime_type is not None:
            for match_type in cls.MIME_TYPES:
                match_type = normalize_mimetype(match_type, default=None)
                if match_type == mime_type:
                    return cls.SCORE

        extensions = [normalize_extension(e) for e in cls.EXTENSIONS]
        extensions = [e for e in extensions if e is not None]
        if normalize_extension(file_path) in extensions:
            return cls.SCORE

        return -1
