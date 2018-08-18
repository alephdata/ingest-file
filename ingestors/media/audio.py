import logging
from pymediainfo import MediaInfo

from ingestors.base import Ingestor
from ingestors.media.util import MediaInfoDateMixIn

log = logging.getLogger(__name__)


class AudioIngestor(Ingestor, MediaInfoDateMixIn):
    MIME_TYPES = [
        'audio/mpeg',
        'audio/mp3',
        'audio/x-m4a',
        'audio/x-hx-aac-adts',
        'audio/x-wav',
        'audio/mp4',
        'audio/ogg',
        'audio/vnd.wav',
        'audio/flac',
        'audio/x-ms-wma',
        'audio/webm',
    ]
    EXTENSIONS = [
        'wav',
        'mp3',
        'aac',
        'ac3',
        'm4a',
        'm4b',
        'ogg',
        'opus',
        'flac',
        'wma',
    ]
    SCORE = 3

    def ingest(self, file_path):
        self.result.flag(self.result.FLAG_AUDIO)
        log.info("[%s] flagged as audio.", self.result)
        metadata = MediaInfo.parse(file_path)
        for track in metadata.tracks:
            self.update('title', track.title)
            self.update('generator', track.writing_application)
            self.update('generator', track.writing_library)
            self.update('generator', track.publisher)
            self.update('created_at', self.parse_date(track.recorded_date))
            self.update('created_at', self.parse_date(track.tagged_date))
            self.update('created_at', self.parse_date(track.encoded_date))
            modified_at = self.parse_date(track.file_last_modification_date)
            self.update('modified_at', modified_at)
            if track.sampling_rate:
                self.update('sampling_rate', str(track.sampling_rate/1000.0))
            self.update('duration', track.duration)

    @classmethod
    def match(cls, file_path, result=None):
        score = super(AudioIngestor, cls).match(file_path, result=result)
        if score <= 0:
            if result.mime_type.startswith('audio/'):
                    return cls.SCORE * 2
        return score
