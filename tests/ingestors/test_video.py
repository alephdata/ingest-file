# -*- coding: utf-8 -*-
import datetime
from ..support import TestCase


class VideoIngestorTest(TestCase):

    def test_video(self):
        fixture_path, entity = self.fixture('big_buck_bunny.mp4')
        result = self.manager.ingest(fixture_path, entity)
        self.assertEqual(
            result.first('processingStatus'),
            self.manager.STATUS_SUCCESS
        )
        self.assertIn('Hinted Video Track', result.get('title'))
        self.assertIn(
            datetime.datetime(2010, 2, 9, 1, 55, 39).isoformat(),
            result.get('authoredAt')
        )
        self.assertEqual(result.first('duration'), '60095')
        self.assertEqual(result.schema, 'Video')
