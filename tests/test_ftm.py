# -*- coding: utf-8 -*-

from .support import TestCase


class FtMIngestorTest(TestCase):
    def test_match(self):
        fixture_path, entity = self.fixture("ofac.json")
        self.manager.ingest(fixture_path, entity)
        self.assertEqual(entity.first("mimeType"), "application/json+ftm")
        self.assertEqual(len(self.manager.entities), 10 + 1)
