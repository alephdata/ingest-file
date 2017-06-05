import logging

log = logging.getLogger(__name__)


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
