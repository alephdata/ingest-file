import logging

from ingestors.base import Ingestor

log = logging.getLogger(__name__)


class VideoIngestor(Ingestor):
    MIME_TYPES = [
        'application/x-shockwave-flash',
        'video/quicktime',
        'video/mp4',
        'video/x-flv',
    ]
    EXTENSIONS = [
        'avi',
        'mpg',
        'mpeg',
        'mkv'
    ]
    SCORE = 3

    def ingest(self, file_path):
        self.result.flag(self.result.FLAG_VIDEO)
        log.info("[%s] flagged as video.", self.result)
