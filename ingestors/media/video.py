import logging
from datetime import datetime
from followthemoney import model
from pymediainfo import MediaInfo
from normality import stringify

from ingestors.ingestor import Ingestor
from ingestors.support.timestamp import TimestampSupport
from ingestors.exc import ProcessingException
from ingestors.support.transcription import TranscriptionSupport

log = logging.getLogger(__name__)


class VideoIngestor(Ingestor, TimestampSupport, TranscriptionSupport):
    MIME_TYPES = [
        "application/x-shockwave-flash",
        "video/quicktime",
        "video/mp4",
        "video/x-flv",
    ]
    EXTENSIONS = [
        "avi",
        "mpg",
        "mpeg",
        "mkv",
        "mp4",
        "mov",
    ]
    SCORE = 3

    def ingest(self, file_path, entity):
        try:
            entity.schema = model.get("Video")
            log.info("[%r] flagged as video.", entity)
            metadata = MediaInfo.parse(file_path)
            for track in metadata.tracks:
                entity.add("title", track.title)
                entity.add("generator", track.writing_application)
                entity.add("generator", track.writing_library)
                entity.add("generator", track.publisher)
                entity.add("authoredAt", self.parse_timestamp(track.recorded_date))
                entity.add("authoredAt", self.parse_timestamp(track.tagged_date))
                entity.add("authoredAt", self.parse_timestamp(track.encoded_date))
                modified_at = self.parse_timestamp(track.file_last_modification_date)
                entity.add("modifiedAt", modified_at)
                entity.add("duration", track.duration)
        except Exception as ex:
            raise ProcessingException("Could not read video: %r", ex) from ex
        try:
            start = datetime.now()
            log.info(f"Attempting to transcribe {file_path}")
            audio_only_file = self.extract_audio(file_path)
            self.transcribe(audio_only_file, entity)
            elapsed_time = datetime.now() - start
            # caution! this can't store an elapsed time larger than 24h
            # datetime.seconds capped at [0,86400)
            elapsed_time = divmod(elapsed_time.total_seconds(), 60)[0]
            log.info(
                f"Transcription duration: {elapsed_time} minutes (audio duration: {entity.get('duration')})"
            )
        except Exception as ex:
            # If the transcription fails, the file processing should still count as a success.
            # The existance of a transcription is not mandatory, for now.
            entity.set("processingError", stringify(ex))
            log.error(ex)

    @classmethod
    def match(cls, file_path, entity):
        score = super(VideoIngestor, cls).match(file_path, entity)
        if score <= 0:
            for mime_type in entity.get("mimeType"):
                if mime_type.startswith("video/"):
                    return cls.SCORE * 2
        return score
