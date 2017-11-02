# -*- coding: utf-8 -*-

from ..support import TestCase


class HTMLIngestorTest(TestCase):

    def test_match(self):
        fixture_path = self.fixture('doc.html')
        result = self.manager.ingest(fixture_path)
        self.assertEqual(result.mime_type, 'text/html')

    def test_ingest_on_unicode_file(self):
        fixture_path = self.fixture('doc.html')
        result = self.manager.ingest(fixture_path)

        self.assertEqual(
            result.body_text,
            'Ingestors Test web page. The GitHub page.'  # noqa
        )
        self.assertEqual(result.title, u'Ingestors Title')
        self.assertEqual(result.summary, u'Ingestors description')
        self.assertEqual(set(result.keywords),
                         set(['ingestors', 'key', 'words', 'news']))

    def test_ingest_extra_fixture(self):
        fixture_path = self.fixture(u'EDRM Micro Datasets « EDRM.htm')
        result = self.manager.ingest(fixture_path)

        self.assertIn(
            'Creating Practical Resources to Improve E-Discovery',
            result.body_text,
        )
        self.assertEqual(result.title, u'EDRM Micro Datasets \xab EDRM')
        self.assertIsNone(result.summary)
        self.assertEqual(result.keywords, [])
        self.assertEqual(result.status, result.STATUS_SUCCESS)

    def test_ingest_empty(self):
        fixture_path = self.fixture(u'empty_5_doc_pages.html')
        result = self.manager.ingest(fixture_path)

        self.assertEqual(result.body_text, '')
        self.assertIsNone(result.title)
        self.assertEqual(result.keywords, [])
        self.assertEqual(result.status, result.STATUS_SUCCESS)
