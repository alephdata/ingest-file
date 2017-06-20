# -*- coding: utf-8 -*-

from ..support import TestCase


class PDFIngestorTest(TestCase):

    def test_match(self):
        fixture_path = self.fixture('readme.pdf')
        result = self.manager.ingest(fixture_path)
        self.assertEqual(result.mime_type, 'application/pdf')

    def test_match_empty(self):
        fixture_path = self.fixture('empty.pdf')
        result = self.manager.ingest(fixture_path)
        self.assertNotEqual(result.mime_type, 'application/pdf')

    def test_ingest_binary_mode(self):
        fixture_path = self.fixture('readme.pdf')
        result = self.manager.ingest(fixture_path)

        self.assertEqual(len(result.pages), 1)
        self.assertIn(
            'Ingestors extract useful information'
            ' in a structured standard format',
            result.pages[0]['text']
        )

    def test_ingest_noisy_fixture(self):
        fixture_path = self.fixture('500 pages.pdf')
        result = self.manager.ingest(fixture_path)
        self.assertEqual(len(result.pages), 500)
        self.assertEqual(
            result.pages[0]['text'],
            'Hello, World! \nHello, World!'
        )

    def test_ingest_complex_fixture(self):
        fixture_path = self.fixture('very_complex_math_book.pdf')
        result = self.manager.ingest(fixture_path)

        self.assertEqual(len(result.pages), 588)
        self.assertIn(
            'ALGEBRA \nABSTRACT \nAND \nCONCRETE \nE \nDITION \n2.6',
            result.pages[0]['text']
        )

    def test_ingest_unicode_fixture(self):
        fixture_path = self.fixture('udhr_ger.pdf')
        result = self.manager.ingest(fixture_path)

        self.assertEqual(len(result.pages), 6)
        self.assertIn(
            u'Würde und der gleichen und unveräußerlichen',
            result.pages[0]['text']
        )
