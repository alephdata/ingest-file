# -*- coding: utf-8 -*-
import datetime
from ..support import TestCase


class VideoIngestorTest(TestCase):

    def test_video(self):
        fixture_path = self.fixture('big_buck_bunny.mp4')
        result = self.manager.ingest(fixture_path)
        self.assertEqual(result.status, result.STATUS_SUCCESS)
        self.assertEqual(result.title, 'Hinted Video Track')
        self.assertEqual(
            result.created_at, datetime.datetime(2010, 2, 9, 1, 55, 40)
        )
        self.assertEqual(result.duration, '60095')
        self.assertIn('video', result.flags)
