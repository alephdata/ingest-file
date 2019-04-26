# -*- coding: utf-8 -*-
import datetime
from ..support import TestCase


class AudioIngestorTest(TestCase):

    def test_audio(self):
        fixture_path, entity = self.fixture('memo.m4a')
        result = self.manager.ingest(fixture_path, entity)
        self.assertEqual(
            result.first('processingStatus'),
            self.manager.STATUS_SUCCESS
        )
        self.assertEqual(result.first('title'), 'Core Media Audio')
        self.assertEqual(
            result.first('generator'), 'com.apple.VoiceMemos (iOS 11.4)'
        )
        self.assertEqual(
            result.first('authoredAt'),
            datetime.datetime(2018, 6, 20, 12, 9, 42).isoformat()
        )
        self.assertEqual(result.first('duration'), '2808')
        self.assertEqual(result.first('samplingRate'), '44100')
        self.assertEqual(result.schema, 'Audio')
