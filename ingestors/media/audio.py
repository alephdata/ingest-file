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


class AudioIngestor(Ingestor, TimestampSupport, TranscriptionSupport):
    MIME_TYPES = [
        "audio/mpeg",
        "audio/mp3",
        "audio/x-m4a",
        "audio/x-hx-aac-adts",
        "audio/x-wav",
        "audio/mp4",
        "audio/ogg",
        "audio/vnd.wav",
        "audio/flac",
        "audio/x-ms-wma",
        "audio/webm",
    ]
    EXTENSIONS = [
        "wav",
        "mp3",
        "aac",
        "ac3",
        "m4a",
        "m4b",
        "ogg",
        "opus",
        "flac",
        "wma",
    ]
    SCORE = 3

    def ingest(self, file_path, entity):
        try:
            entity.schema = model.get("Audio")
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
                if track.sampling_rate:
                    entity.add("samplingRate", track.sampling_rate)
                entity.add("duration", track.duration)
        except Exception as ex:
            raise ProcessingException(f"Could not read audio: {ex}") from ex
        try:
            start = datetime.now()
            log.info(f"Attempting to transcribe {file_path}")
            self.transcribe(file_path, entity)
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
        score = super(AudioIngestor, cls).match(file_path, entity)
        if score <= 0:
            for mime_type in entity.get("mimeType"):
                if mime_type.startswith("audio/"):
                    return cls.SCORE * 2
        return score
