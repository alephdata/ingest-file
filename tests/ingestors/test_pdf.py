# -*- coding: utf-8 -*-
import io
from unittest import skipUnless

from ingestors.pdf import Ingestor, PDFIngestor

from ..support import TestCase


class PDFIngestorTest(TestCase):

    def test_match(self):
        fixture_path = self.fixture('readme.pdf')

        with io.open(fixture_path, mode='rb') as fio:
            ingestor_class, mime_type = Ingestor.match(fio)

        self.assertTrue(issubclass(ingestor_class, Ingestor))
        self.assertIs(ingestor_class, PDFIngestor)
        self.assertEqual(mime_type, 'application/pdf')

    def test_ingest_binary_mode(self):
        fixture_path = self.fixture('readme.pdf')

        with io.open(fixture_path, mode='rb') as fio:
            ing = PDFIngestor(fio, fixture_path)
            ing.run()

        self.assertIsNone(ing.result.content)
        self.assertEqual(len(ing.detached), 1)
        self.assertIn(
            'Ingestors extract useful information'
            ' in a structured standard format',
            ing.detached[0].result.content
        )

    @skipUnless(TestCase.EXTRA_FIXTURES, 'No extra fixtures.')
    def test_ingest_noisy_fixture(self):
        fixture_path = self.fixture(
            'documents/pdf/HelloWorld with color squares in 500 pages.pdf')

        with io.open(fixture_path, mode='rb') as fio:
            ing = PDFIngestor(fio, fixture_path)
            ing.run()

        self.assertIsNone(ing.result.content)
        self.assertEqual(len(ing.detached), 500)
        self.assertEqual(
            ing.detached[0].result.content,
            'Hello, World!\nHello, World!'
        )

    @skipUnless(TestCase.EXTRA_FIXTURES, 'No extra fixtures.')
    def test_ingest_complex_fixture(self):
        fixture_path = self.fixture('bad/very_complex_math_book.pdf')

        with io.open(fixture_path, mode='rb') as fio:
            ing = PDFIngestor(fio, fixture_path)
            ing.run()

        self.assertIsNone(ing.result.content)
        self.assertEqual(len(ing.detached), 588)
        self.assertIn(
            'ALGEBRA\nABSTRACT\nAND\nCONCRETE\nE\nDITION\n2.6',
            ing.detached[0].result.content
        )

    @skipUnless(TestCase.EXTRA_FIXTURES, 'No extra fixtures.')
    def test_ingest_unicode_fixture(self):
        fixture_path = self.fixture('languages/udhr_ger.pdf')

        with io.open(fixture_path, mode='rb') as fio:
            ing = PDFIngestor(fio, fixture_path)
            ing.run()

        self.assertIsNone(ing.result.content)
        self.assertEqual(len(ing.detached), 6)
        self.assertIn(
            u'Würde und der gleichen und unveräußerlichen',
            ing.detached[0].result.content
        )

        cur_page = 1
        for detached in ing.detached:
            self.assertEqual(detached.result.order, cur_page)
            self.assertEqual(detached.status, PDFIngestor.STATUSES.SUCCESS)
            self.assertEqual(detached.state, PDFIngestor.STATES.FINISHED)
            cur_page += 1

    @skipUnless(TestCase.EXTRA_FIXTURES, 'No extra fixtures.')
    def test_ingest_noisy_blank_fixture(self):
        fixture_path = self.fixture('large/noise images in 15 pages.pdf')

        with io.open(fixture_path, mode='rb') as fio:
            ing = PDFIngestor(fio, fixture_path)
            ing.run()

        self.assertIsNone(ing.result.content)
        self.assertEqual(len(ing.detached), 15)

        for detached in ing.detached:
            self.assertIsNone(detached.result.content)
