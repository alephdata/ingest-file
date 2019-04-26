# -*- coding: utf-8 -*-

from ..support import TestCase


class PDFIngestorTest(TestCase):

    def test_match(self):
        fixture_path, entity = self.fixture('readme.pdf')
        result = self.manager.ingest(fixture_path, entity)
        self.assertEqual(result.first('mimeType'), 'application/pdf')

    def test_match_empty(self):
        fixture_path, entity = self.fixture('empty.pdf')
        result = self.manager.ingest(fixture_path, entity)
        self.assertNotEqual(result.first('mimeType'), 'application/pdf')

    def test_ingest_binary_mode(self):
        fixture_path, entity = self.fixture('readme.pdf')
        result = self.manager.ingest(fixture_path, entity)

        self.assertEqual(len(self.manager.entities), 1 + 1)
        self.assertIn(
            'Ingestors extract useful information'
            ' in a structured standard format',
            self.manager.entities[0].first('bodyText')
        )
        self.assertEqual(result.schema, 'Pages')

    def test_ingest_noisy_fixture(self):
        fixture_path, entity = self.fixture('500 pages.pdf')
        result = self.manager.ingest(fixture_path, entity)
        self.assertEqual(len(self.manager.entities), 500 + 1)
        self.assertEqual(
            self.manager.entities[0].first('bodyText'),
            'Hello, World! \nHello, World!'
        )
        self.assertEqual(result.schema, 'Pages')

    def test_ingest_complex_fixture(self):
        fixture_path, entity = self.fixture('very_complex_math_book.pdf')
        self.manager.ingest(fixture_path, entity)

        self.assertEqual(len(self.manager.entities), 588 + 1)
        self.assertIn(
            'ALGEBRA \nABSTRACT AND CONCRETE \nE DITION 2.6',
            self.manager.entities[0].first('bodyText')
        )

    def test_ingest_unicode_fixture(self):
        fixture_path, entity = self.fixture('udhr_ger.pdf')
        self.manager.ingest(fixture_path, entity)

        self.assertEqual(len(self.manager.entities), 6 + 1)
        self.assertIn(
            u'Würde und der gleichen und unveräußerlichen',
            self.manager.entities[0].first('bodyText')
        )
