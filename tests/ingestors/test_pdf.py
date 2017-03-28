# -*- coding: utf-8 -*-
import io
from unittest import skipUnless

from ingestors.pdf import PDFIngestor

from ..support import TestCase


class PDFIngestorTest(TestCase):

    def test_ingest_binary_mode(self):
        fixture_path = self.fixture('readme.pdf')

        with io.open(fixture_path, mode='rb') as fio:
            ing = PDFIngestor(fio, fixture_path)
            ing.run()

        self.assertIsNotNone(ing.result.content)
        self.assertIn(
            'Ingestors extract useful information'
            ' in a structured standard format',
            ing.result.content
        )

    @skipUnless(TestCase.EXTRA_FIXTURES, 'No extra fixtures.')
    def test_ingest_extra_fixture(self):
        fixture_path = self.fixture(
            'documents/pdf/HelloWorld with color squares in 500 pages.pdf')

        with io.open(fixture_path, mode='rb') as fio:
            ing = PDFIngestor(fio, fixture_path)
            ing.run()

        self.assertIsNone(ing.result.content)
