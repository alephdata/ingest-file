import logging
from pymediainfo import MediaInfo

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
        'mkv',
        'mp4',
        'mov',
    ]
    SCORE = 3

    def ingest(self, file_path):
        self.result.flag(self.result.FLAG_VIDEO)
        log.info("[%s] flagged as video.", self.result)
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
            self.update('duration', track.duration)

    @classmethod
    def match(cls, file_path, result=None):
        score = super(VideoIngestor, cls).match(file_path, result=result)
        if score <= 0:
            if result.mime_type.startswith('video/'):
                    return cls.SCORE * 2
        return score
