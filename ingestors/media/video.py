import logging
import datetime

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
            for val in (
                track.encoded_date, track.tagged_date, track.recorded_date
            ):
                if val:
                    date = datetime.datetime.strptime(val, "%Z %Y-%m-%d %H:%M:%S")
                    self.update('created_at', date)
                    break
            if track.file_last_modification_date:
                date = datetime.datetime.strptime(
                    track.file_last_modification_date, "%Z %Y-%m-%d %H:%M:%S"
                )
                self.update('modified_at', date)
            self.update('duration', track.duration)

    @classmethod
    def match(cls, file_path, result=None):
        score = super(VideoIngestor, cls).match(file_path, result=result)
        if score <= 0:
            if result.mime_type.startswith('video/'):
                    return cls.SCORE * 2
        return score
