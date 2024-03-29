# -*- coding: utf-8 -*-
from datetime import datetime

from .support import TestCase


class DocumentIngestorTest(TestCase):
    def test_match(self):
        fixture_path, entity = self.fixture("hello world word.docx")
        self.manager.ingest(fixture_path, entity)
        self.assertEqual(
            entity.first("mimeType"),
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # noqa
        )
        self.assertEqual(entity.schema.name, "Pages")

    def test_ingest_word_doc(self):
        fixture_path, entity = self.fixture("doc.doc")
        self.manager.ingest(fixture_path, entity)

        self.assertEqual(len(self.get_emitted()), 3)
        self.assertEqual(
            len(list(self.manager.dataset.iterate(entity_id=entity.id))), 1
        )
        self.assertTrue(
            any(
                "The Level 3 Bookmark" in x
                for x in self.manager.dataset.get(entity_id=entity.id).get("indexText")
            )
        )
        self.assertIn(
            "This is a sample Microsoft Word Document.",
            self.manager.entities[0].first("bodyText"),
        )

        self.assertIn(
            "The Level 3 Bookmark", self.manager.entities[2].first("bodyText")
        )
        self.assertEqual(entity.schema.name, "Pages")

    def test_ingest_presentation_doc(self):
        fixture_path, entity = self.fixture("slides.ppt")
        self.manager.ingest(fixture_path, entity)

        today = datetime.now()

        self.assertEqual(len(self.get_emitted()), 2)
        self.assertIn("Now", self.manager.entities[0].first("bodyText"))
        self.assertEqual(entity.schema.name, "Pages")
        self.assertIn(today.strftime("%x"), self.manager.entities[0].first("bodyText"))

    def test_ingest_encrypted_doc(self):
        fixture_path, entity = self.fixture("encypted_by_libreoffice.odt")
        self.manager.ingest(fixture_path, entity)

        self.assertEqual(entity.first("processingStatus"), self.manager.STATUS_FAILURE)

    def test_ingest_odt_fail(self):
        fixture_path, entity = self.fixture("rand-1670433101.440986000.odt")
        self.manager.ingest(fixture_path, entity)

        assert (
            "graphomaniac Talpa Deuteronomical tubber johannite"
            in self.manager.entities[0].first("bodyText")
        )

    def test_ingest_noisy_doc(self):
        fixture_path, entity = self.fixture("Plan.odt")
        self.manager.ingest(fixture_path, entity)
        self.assertEqual(len(self.get_emitted()), 2)
        self.assertIn(
            "We should paint graffiti on all corners",
            self.manager.entities[0].first("bodyText"),
        )
        self.assertEqual(entity.first("processingStatus"), self.manager.STATUS_SUCCESS)
