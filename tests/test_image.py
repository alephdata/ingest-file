from .support import TestCase


class ImageIngestorTest(TestCase):
    def test_match(self):
        fixture_path, entity = self.fixture("image.svg")
        self.manager.ingest(fixture_path, entity)
        self.assertEqual(entity.first("mimeType"), "image/svg+xml")

    def test_ingest_on_svg(self):
        fixture_path, entity = self.fixture("image.svg")
        self.manager.ingest(fixture_path, entity)

        self.assertIn("TEST", entity.first("bodyText"))
        self.assertEqual(entity.first("processingStatus"), self.manager.STATUS_SUCCESS)

    def test_ingest_on_jpeg(self):
        fixture_path, entity = self.fixture("jpegtest.jpg")
        self.manager.ingest(fixture_path, entity)
        import tesserocr

        self.assertIn(
            "Debian",
            entity.first("bodyText"),
            f"tesserocr version: {tesserocr.tesseract_version()}",
        )
        self.assertEqual(entity.first("mimeType"), "image/jpeg")

        self.assertEqual(entity.first("processingStatus"), self.manager.STATUS_SUCCESS)
