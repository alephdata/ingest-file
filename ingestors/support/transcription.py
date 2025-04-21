import json
import logging
import subprocess
from pathlib import Path

from ingestors import settings
from ingestors.exc import ProcessingException

log = logging.getLogger(__name__)


class TranscriptionSupport:
    """Provides a helper for transcribing audio and video files."""

    def extract_audio(self, file_path):
        audio_only_path = Path("/ingestors") / file_path.parts[-1].split(".")[0]
        audio_only_path = audio_only_path.with_suffix(".wav")

        # https://github.com/ggml-org/whisper.cpp?tab=readme-ov-file#quick-start
        cmd = [
            "ffmpeg",
            "-i",
            file_path,
            "-ar",
            "16000",
            "-ac",
            "1",
            "-c:a",
            "pcm_s16le",
            audio_only_path,
        ]

        try:
            subprocess.run(
                cmd, timeout=settings.WHISPER_TRANSCRIPTION_TIMEOUT, check=True
            )
        except subprocess.CalledProcessError as e:
            raise e

        if not audio_only_path.is_file():
            raise ProcessingException("Audio extraction failed.")

        return audio_only_path

    def transcribe(self, file_path, entity):
        model = settings.WHISPER_MODEL

        models_path = Path("/whisper/models")

        output_path = Path("/ingestors") / file_path.parts[-1].split(".")[0]

        cmd = [
            "/whisper/build/bin/whisper-cli",
            "-m",
            models_path / model,
            "-f",
            file_path,
            "-oj",
            "-of",
            output_path,
            "-l",
            # setting to "auto" sometimes transcribes audio in an unintended language
            settings.WHISPER_LANGUAGE,
        ]

        try:
            log.info(cmd)
            subprocess.run(
                cmd, timeout=int(settings.WHISPER_TRANSCRIPTION_TIMEOUT), check=True
            )
        except subprocess.CalledProcessError as e:
            raise e
        # if the transcription succeeded, the output is written to a JSON
        output_path = output_path.with_suffix(".json")
        if not output_path.is_file():
            raise ProcessingException(
                f"Transcription failed. The file type might be unsupported for {file_path.parts[-1]}."
            )

        with open(output_path, "r") as f:
            transcription_dict = json.loads(f.read())

        transcription_intervals = transcription_dict.get("transcription")
        if transcription_intervals:
            full_transcription = ""
            for interval in transcription_intervals:
                full_transcription += f"[{interval['timestamps']['from']} -> {interval['timestamps']['to']}] {interval['text'].strip()}"
            entity.add("indexText", full_transcription)

        else:
            self.delete_temporary_file(output_path)
            raise ProcessingException(
                f"Transcription failed, no output in file {output_path}."
            )

        self.delete_temporary_file(output_path)

    def delete_temporary_file(self, file_path):
        if not file_path.is_file():
            return

        Path.unlink(file_path)
