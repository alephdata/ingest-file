# -*- coding: utf-8 -*-
import datetime
from unittest import mock

from .support import TestCase, TranscriptionSupport_


class VideoIngestorTest(TestCase):
    def test_video(self):
        fixture_path, entity = self.fixture("big_buck_bunny.mp4")

        # Mock the transcription class because running the code takes a very long time
        patcher = mock.patch(
            "ingestors.support.transcription.TranscriptionSupport",
            new=TranscriptionSupport_,
        )
        patcher.start()
        self.manager.ingest(fixture_path, entity)
        patcher.stop()

        self.assertEqual(entity.first("processingStatus"), self.manager.STATUS_SUCCESS)
        self.assertIn("Hinted Video Track", entity.get("title"))
        self.assertIn(
            datetime.datetime(2010, 2, 9, 1, 55, 39).isoformat(),
            entity.get("authoredAt"),
        )
        self.assertEqual(entity.first("duration"), "60095")
        self.assertEqual(entity.schema.name, "Video")
