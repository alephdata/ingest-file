# -*- coding: utf-8 -*-
from ..support import TestCase


class VideoIngestorTest(TestCase):

    def test_video(self):
        fixture_path = self.fixture('big_buck_bunny.mp4')
        result = self.manager.ingest(fixture_path)
        self.assertEqual(result.status, result.STATUS_SUCCESS)
        self.assertEqual(result.title, 'Hinted Video Track')
        self.assertEqual(result.created_at, 'UTC 2010-02-09 01:55:39')
        self.assertEqual(result.duration, '60095')
        self.assertIn('video', result.flags)
