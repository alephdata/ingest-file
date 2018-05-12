import logging

from ingestors.base import Ingestor

log = logging.getLogger(__name__)


class AudioIngestor(Ingestor):
    MIME_TYPES = [
        'audio/mpeg',
        'audio/mp3',
        'audio/x-m4a',
        'audio/x-hx-aac-adts',
        'audio/x-wav',
    ]
    EXTENSIONS = [
        'wav',
        'mp3',
        'aac'
    ]
    SCORE = 3

    def ingest(self, file_path):
        # TODO: ID3
        self.result.flag(self.result.FLAG_AUDIO)
        log.info("[%s] flagged as audio.", self.result)
