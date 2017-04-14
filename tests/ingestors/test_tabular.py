# -*- coding: utf-8 -*-
import io
from datetime import datetime
from unittest import skipUnless

from ingestors.tabular import TabularIngestor

from ..support import TestCase


class TabularIngestorTest(TestCase):

    def test_ingest_excel_file(self):
        fixture_path = self.fixture('file.xlsx')

        with io.open(fixture_path, mode='rb') as fio:
            ing = TabularIngestor(fio, fixture_path)
            ing.run()

        self.assertIsNone(ing.result.content)
        self.assertEqual(len(ing.children), 2)
        self.assertEqual(
            ing.result.columns['Sheet1'], [u'Name', u'Timestamp', u'Price'])
        self.assertEqual(
            ing.result.columns['Sheet2'], [u'Title', u'Price', u'Timestamp'])

        self.assertEqual(ing.children[0].result.sheet_name, 'Sheet1')
        self.assertEqual(ing.children[0].result.sheet_number, 0)
        self.assertEqual(ing.children[0].result.page, 0)
        self.assertEqual(dict(ing.children[0].result.content), {
            u'Name': u'Mihai Viteazul',
            u'Timestamp': datetime(1871, 12, 29, 13, 48),
            u'Price': 11.99
        })

        self.assertEqual(ing.children[1].result.sheet_name, 'Sheet2')
        self.assertEqual(ing.children[1].result.sheet_number, 1)
        self.assertEqual(ing.children[1].result.page, 1)
        self.assertEqual(ing.children[1].result.content, {
            u'Title': u'Vlad Țepeș',
            u'Timestamp': datetime(1953, 9, 13, 22, 1),
            u'Price': 111
        })

    @skipUnless(TestCase.EXTRA_FIXTURES, 'No extra fixtures.')
    def test_ingest_csv_fixture(self):
        fixture_path = self.fixture('efi/Concordance Load File.csv')

        with io.open(fixture_path, mode='rb') as fio:
            ing = TabularIngestor(fio, fixture_path)
            ing.run()

        self.assertEqual(len(ing.children), 4)
        self.assertEqual(
            ing.result.columns['table'],
            [u'BEGDOC', u'ENDDOC', u'FILENAME',
             u'MODDATE', u'AUTHOR', u'DOCTYPE']
        )
        self.assertEqual(ing.children[0].result.sheet_name, 'table')
        self.assertEqual(ing.children[0].result.sheet_number, 0)
        self.assertEqual(ing.children[0].result.page, 0)
        self.assertEqual(dict(ing.children[0].result.content), {
            u'AUTHOR': u'J. Smith',
            u'BEGDOC': 1,
            u'DOCTYPE': u'docx',
            u'ENDDOC': 4,
            u'FILENAME': u'Contract',
            u'MODDATE': datetime(2013, 1, 12, 0, 0)
        })
