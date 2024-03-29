# -*- coding: utf-8 -*-

from .support import TestCase


class HTMLIngestorTest(TestCase):
    def test_match(self):
        fixture_path, entity = self.fixture("doc.html")
        self.manager.ingest(fixture_path, entity)
        self.assertEqual(entity.first("mimeType"), "text/html")

    def test_ingest_on_unicode_file(self):
        fixture_path, entity = self.fixture("doc.html")
        self.manager.ingest(fixture_path, entity)

        self.assertEqual(
            entity.first("indexText"),
            "Ingestors Test web page. The GitHub page.",  # noqa
        )
        self.assertEqual(entity.first("title"), "Ingestors Title")
        self.assertEqual(entity.first("summary"), "Ingestors description")
        self.assertEqual(
            set(entity.get("keywords")), set(["ingestors", "key", "words", "news"])
        )

    def test_ingest_extra_fixture(self):
        fixture_path, entity = self.fixture("EDRM Micro Datasets « EDRM.htm")
        self.manager.ingest(fixture_path, entity)

        self.assertIn(
            "Creating Practical Resources to Improve E-Discovery",
            entity.first("indexText"),
        )
        self.assertEqual(entity.first("title"), "EDRM Micro Datasets \xab EDRM")
        self.assertIsNone(entity.first("summary"))
        self.assertEqual(entity.get("keywords"), [])
        self.assertEqual(entity.first("processingStatus"), self.manager.STATUS_SUCCESS)

    def test_ingest_empty(self):
        fixture_path, entity = self.fixture("empty_5_doc_pages.html")
        self.manager.ingest(fixture_path, entity)

        self.assertEqual(entity.first("indexText"), None)
        self.assertIsNone(entity.first("title"))
        self.assertEqual(entity.get("keywords"), [])
        self.assertEqual(entity.first("processingStatus"), self.manager.STATUS_SUCCESS)
