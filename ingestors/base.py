import logging
from tempfile import mkdtemp
from datetime import date, datetime
from celestial import normalize_mimetype
from ingestors.util import normalize_extension
from ingestors.util import safe_string, remove_directory

log = logging.getLogger(__name__)


class Ingestor(object):
    """Generic ingestor class."""
    MIME_TYPES = []
    EXTENSIONS = []
    SCORE = 3

    def __init__(self, manager, result, work_path=None):
        self.manager = manager
        self.result = result
        if work_path is None:
            work_path = mkdtemp(prefix='ingestor-')
        self.work_path = work_path

    def ingest(self, file_path):
        """The ingestor implementation. Should be overwritten.

        This method does not return anything.
        Use the ``result`` attribute to store any resulted data.
        """
        raise NotImplemented()

    def cleanup(self):
        remove_directory(self.work_path)

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
        if not hasattr(cls, '_MIME_TYPES'):
            cls._MIME_TYPES = [normalize_mimetype(m, default=None) for m in cls.MIME_TYPES]  # noqa
            cls._MIME_TYPES = [m for m in cls._MIME_TYPES if m is not None]

        mime_type = normalize_mimetype(result.mime_type, default=None)
        if mime_type in cls._MIME_TYPES:
            return cls.SCORE

        cls._EXTENSIONS = [normalize_extension(e) for e in cls.EXTENSIONS]
        cls._EXTENSIONS = [e for e in cls._EXTENSIONS if e is not None]

        extension = normalize_extension(result.file_name)
        if extension in cls._EXTENSIONS:
            return cls.SCORE

        return -1
