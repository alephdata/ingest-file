# -*- coding: utf-8 -*-

from .support import TestCase


class PDFIngestorTest(TestCase):
    def test_match(self):
        fixture_path, entity = self.fixture("readme.pdf")
        self.manager.ingest(fixture_path, entity)
        self.assertEqual(entity.first("mimeType"), "application/pdf")

    def test_match_empty(self):
        fixture_path, entity = self.fixture("empty.pdf")
        self.manager.ingest(fixture_path, entity)
        self.assertNotEqual(entity.first("mimeType"), "application/pdf")

    def test_ingest_binary_mode(self):
        fixture_path, entity = self.fixture("readme.pdf")
        self.manager.ingest(fixture_path, entity)

        # 2 doc fragments, 1 page
        self.assertEqual(len(self.get_emitted()), 2)
        self.assertIn(
            "Ingestors extract useful information" " in a structured standard format",
            self.manager.entities[0].first("bodyText"),
        )
        entities = list(self.manager.dataset.iterate(entity_id=entity.id))
        self.assertEqual(len(entities), 1)
        text = entities[0].first("indexText")
        self.assertIn("Ingestors extract useful information", text)

    def test_ingest_noisy_fixture(self):
        fixture_path, entity = self.fixture("500 pages.pdf")
        self.manager.ingest(fixture_path, entity)
        self.assertEqual(len(self.get_emitted()), 501)
        self.assertEqual(
            self.manager.entities[0].first("bodyText"), "Hello, World!\nHello, World!"
        )
        self.assertEqual(entity.schema.name, "Pages")

    def test_ingest_complex_fixture(self):
        fixture_path, entity = self.fixture("very_complex_math_book.pdf")
        self.manager.ingest(fixture_path, entity)

        self.assertEqual(len(self.get_emitted()), 589)
        body = self.manager.entities[0].first("bodyText")
        self.assertIn("ALGEBRA", body)
        self.assertIn("ABSTRACT AND CONCRETE", body)
        self.assertIn("Last revised on February 4, 2014.", body)

        page_two = self.manager.entities[2].first("bodyText")
        assert (
            "The author reserves all rights to this work not explicitly granted, including the right to copy"
            in page_two
        )
        assert (
            "Algebra: abstract and concrete / Frederick M. Goodman— ed. 2" in page_two
        )
        assert "ISBN 978-0-9799142-1-8" in page_two

        assert any(
            [
                line
                for line in self.manager.entities[5].get("indexText")
                if "A Note to the Reader" in line
            ]
        )

    def test_ingest_unicode_fixture(self):
        fixture_path, entity = self.fixture("udhr_ger.pdf")
        self.manager.ingest(fixture_path, entity)

        self.assertEqual(len(self.get_emitted()), 7)
        self.assertIn(
            "Würde und der gleichen und unveräußerlichen",
            self.manager.entities[0].first("bodyText"),
        )

    def test_ingest_protected(self):
        fixture_path, entity = self.fixture("password-hunter2.pdf")
        self.manager.ingest(fixture_path, entity)

        self.assertEqual(len(self.get_emitted()), 1)
        text = self.manager.entities[0].first("bodyText")
        self.assertEqual(None, text)
        err = self.manager.entities[0].first("processingError")
        self.assertIn(
            "Could not extract PDF file. The PDF is protected with a password. Try removing the password protection and re-uploading the documents.",
            err,
        )
        status = self.manager.entities[0].first("processingStatus")
        self.assertEqual("failure", status)

    def test_jbig2(self):
        fixture_path, entity = self.fixture("jbig2.pdf")
        self.manager.ingest(fixture_path, entity)

        self.assertEqual(len(self.get_emitted()), 6)
        self.assertIn(
            "ImageMagick does not support JBIG2 compression for PDF image files.",
            self.manager.entities[0].first("bodyText"),
        )
        self.assertIn(
            "think JBIG2 is there now.",
            self.manager.entities[2].first("bodyText"),
        )
        self.assertIn(
            "The fact that the PDF format can store images as JBIG2 became",
            self.manager.entities[6].first("bodyText"),
        )

    def test_pdf_conversion_metadata(self):
        fixture_path, entity = self.fixture("hello world word.docx")
        self.manager.ingest(fixture_path, entity)

        self.assertEqual(len(self.get_emitted()), 2)
        self.assertEqual(
            entity.first("mimeType"),
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # noqa
        )
        self.assertEqual(entity.schema.name, "Pages")

        # make sure the metadata we read isn't taken from the converted pdf file
        assert entity.get("authoredAt") == ["2015-09-07T10:57:00"]
        assert entity.get("modifiedAt") == ["2015-10-05T08:57:00"]

    def test_pdf_letter_spacing(self):
        """Checks some tricky word spacing in the fancy food menu."""
        fixture_path, entity = self.fixture("the-dorset-food-menu.pdf")
        self.manager.ingest(fixture_path, entity)

        assert len(self.get_emitted()) == 3

        page_one = self.manager.entities[0]
        page_two = self.manager.entities[2]
        body_one = page_one.first("bodyText")
        body_two = page_two.first("bodyText")
        assert page_one.schema.name == "Page"
        assert page_two.schema.name == "Page"

        for expected_string in [
            "served with marinated olives",
            "made with vegetarian ingredients",
            "triple-cooked chips",
        ]:
            assert expected_string in body_one.lower()

        for expected_string in [
            "burger",
            "triple-cooked chips £4.0",
            "01273605423",
            "bookings@thedorset.co.uk",
            "www.instagram.com/thedorsetbtn/",
        ]:
            assert expected_string in body_two.lower()

    def test_ingest_index_text(self):
        """Make sure that text from all pages shows up in the index."""

        fixture_path, entity = self.fixture("udhr_ger.pdf")
        self.manager.ingest(fixture_path, entity)

        emitted = self.get_emitted()
        assert len(emitted) == 7

        pages_entity = emitted[5]
        assert pages_entity.schema.name == "Pages"

        pages_index = "\n".join(pages_entity.get("indexText"))

        # Page 1
        assert "Da die Anerkennung der angeborenen Würde" in pages_index
        # Page 2
        assert (
            "Jeder hat Anspruch auf alle in dieser Erklärung verkündeten Rechte und Freiheiten"
            in pages_index
        )
        # Page 3
        assert (
            "Jeder hat das Recht, jedes Land, einschließlich seines eigenen, zu verlassen"
            in pages_index
        )
        # Page 4
        assert (
            "Eine Ehe darf nur bei freier und uneingeschränkter Willenseinigung der künftigen"
            in pages_index
        )
        # Page 5
        assert (
            "Jeder hat das Recht auf Erholung und Freizeit und insbesondere auf eine vernünftige"
            in pages_index
        )
        # Page 6
        assert (
            "Erklärung verkündeten Rechte und Freiheiten zum Ziel hat." in pages_index
        )

    def test_ingest_pdf_ocr_greek(self):
        fixture_path, entity = self.fixture("greek.pdf")
        self.manager.ingest(fixture_path, entity)

        emitted = self.get_emitted()
        assert len(emitted) == 3

        page = emitted[1]
        assert page.schema.name == "Page"
        assert "IRIDECEA HOLDINGS LIMITED" in "\n".join(page.get("bodyText"))

    def test_ingest_pdf_normalized(self):
        """The text in this document contains escape sequences like
        \xa0 which need to be normalized in order for search to work. There are
        also some unsupported images embedded which need to be skipped."""

        fixture_path, entity = self.fixture("106972554.pdf")
        self.manager.ingest(fixture_path, entity)

        emitted = self.get_emitted()
        assert len(emitted) == 4

        expected = {
            "1": "UPON THE APPLICATION of the Plaintiff in this action",
            "2": "The 1st, 2nd and 4th Defendants shall jointly",
            "3": "On or around 6 February 2014",
        }

        for page in emitted:
            if page.schema.name == "Pages":
                continue

            assert page.schema.name == "Page"
            page_no = page.properties["index"][0]
            page_text = "\n".join(page.get("bodyText"))

            assert expected[page_no] in page_text
