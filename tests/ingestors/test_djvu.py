# -*- coding: utf-8 -*-
from unittest import skip
from ..support import TestCase


class DejaVuIngestorTest(TestCase):

    @skip
    def test_match(self):
        fixture_path = self.fixture('Test_rs20846.djvu')
        result = self.manager.ingest(fixture_path)
        self.assertEqual(result.mime_type, 'image/vnd.djvu')

        self.assertEqual(len(result.pages), 11)
        self.assertIn(u'Executive Orders', result.pages[0]['text'])
