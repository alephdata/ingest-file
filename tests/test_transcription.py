from unittest import skip

from .support import TestCase


class TranscriptionSupportTest(TestCase):
    @skip
    def test_audio_transcription(self):
        fixture_path, entity = self.fixture("AddressfromFrance.mp3")
        self.manager.ingest(fixture_path, entity)
        self.assertEqual(entity.first("processingStatus"), self.manager.STATUS_SUCCESS)
        self.assertIn(
            "Everything you hold worthwhile is at stake",
            self.manager.entities[0].first("indexText"),
        )
