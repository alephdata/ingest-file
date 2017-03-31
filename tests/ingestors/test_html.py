# -*- coding: utf-8 -*-
import io
from unittest import skipUnless

from ingestors.html import HTMLIngestor

from ..support import TestCase


class HTMLIngestorTest(TestCase):

    def test_ingest_on_unicode_file(self):
        fixture_path = self.fixture('doc.html')

        with io.open(fixture_path, mode='rb') as fio:
            ing = HTMLIngestor(fio, fixture_path)
            ing.run()

        self.assertEqual(
            ing.result.content,
            u'Ingestors\n\nTest web page.\nThe GitHub page.'
        )
        self.assertEqual(ing.result.title, u'Ingestors Title')
        self.assertEqual(ing.result.description, u'Ingestors description')
        self.assertEqual(ing.result.keywords, ['ingestors', 'key', 'words'])
        self.assertEqual(ing.result.news_keywords, ['news', 'key', 'words'])
        self.assertEqual(
            ing.result.urls,
            {'https://github.com/alephdata/ingestors': ['GitHub page']}
        )
        self.assertEqual(ing.status, HTMLIngestor.STATUSES.SUCCESS)
        self.assertEqual(ing.state, HTMLIngestor.STATES.FINISHED)

    @skipUnless(TestCase.EXTRA_FIXTURES, 'No extra fixtures.')
    def test_ingest_extra_fixture(self):
        fixture_path = self.fixture(u'web/EDRM Micro Datasets « EDRM.htm')

        with io.open(fixture_path, mode='rb') as fio:
            ing = HTMLIngestor(fio, fixture_path)
            ing.run()

        self.assertIn(
            'Creating Practical Resources to Improve E-Discovery',
            ing.result.content,
        )
        self.assertEqual(ing.result.title, u'EDRM Micro Datasets \xab EDRM')
        self.assertIsNone(ing.result.description)
        self.assertIsNone(ing.result.keywords)
        self.assertIsNone(ing.result.news_keywords)
        self.assertEqual(ing.status, HTMLIngestor.STATUSES.SUCCESS)
        self.assertEqual(ing.state, HTMLIngestor.STATES.FINISHED)

    @skipUnless(TestCase.EXTRA_FIXTURES, 'No extra fixtures.')
    def test_ingest_empty(self):
        fixture_path = self.fixture(u'formats/empty_5_doc_pages.html')

        with io.open(fixture_path, mode='rb') as fio:
            ing = HTMLIngestor(fio, fixture_path)
            ing.run()

        self.assertEqual(ing.result.content, '')
        self.assertIsNone(ing.result.title)
        self.assertIsNone(ing.result.description)
        self.assertIsNone(ing.result.keywords)
        self.assertIsNone(ing.result.news_keywords)
        self.assertEqual(ing.status, HTMLIngestor.STATUSES.SUCCESS)
        self.assertEqual(ing.state, HTMLIngestor.STATES.FINISHED)

    @skipUnless(TestCase.EXTRA_FIXTURES, 'No extra fixtures.')
    def test_ingest_xml(self):
        fixture_path = self.fixture(u'formats/xml_mini.xml')

        with io.open(fixture_path, mode='rb') as fio:
            ing = HTMLIngestor(fio, fixture_path)
            ing.run()

        self.assertEqual(ing.result.content, '')
        self.assertIsNone(ing.result.title)
        self.assertIsNone(ing.result.description)
        self.assertIsNone(ing.result.keywords)
        self.assertIsNone(ing.result.news_keywords)
        self.assertEqual(ing.status, HTMLIngestor.STATUSES.SUCCESS)
        self.assertEqual(ing.state, HTMLIngestor.STATES.FINISHED)
