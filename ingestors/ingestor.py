import logging
from tempfile import mkdtemp
from datetime import date, datetime
from pantomime import normalize_mimetype, normalize_extension
from ingestors.util import safe_string, remove_directory

log = logging.getLogger(__name__)


class Ingestor(object):
    """Generic ingestor class."""
    MIME_TYPES = []
    EXTENSIONS = []
    SCORE = 3

    def __init__(self, manager, work_path=None):
        self.manager = manager
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

    # def update(self, name, value):
    #     """Set a metadata value if it is not already set with a value."""
    #     existing = getattr(self.result, name)
    #     if existing:
    #         return
    #     if not isinstance(value, (date, datetime)):
    #         value = safe_string(value)
    #     if value is None:
    #         return
    #     setattr(self.result, name, value)

    @classmethod
    def match(cls, file_path, entity):
        mime_types = [normalize_mimetype(m, default=None) for m in cls.MIME_TYPES]  # noqa
        mime_types = [m for m in mime_types if m is not None]
        for mime_type in entity.get('mimeType'):
            if mime_type in mime_types:
                return cls.SCORE

        extensions = [normalize_extension(e) for e in cls.EXTENSIONS]
        for file_name in entity.get('fileName'):
            extension = normalize_extension(file_name)
            if extension is not None and extension in extensions:
                return cls.SCORE

        return -1
