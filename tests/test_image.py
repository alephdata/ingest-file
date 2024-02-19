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

    def test_ingest_hand_written_text(self):
        fixture_path, entity = self.fixture("jpegtest.jpg")
        self.manager.ingest(fixture_path, entity)
        self.assertEqual(len(self.get_emitted()), 1)
        self.assertIn("Debian", self.manager.entities[0].first("bodyText"))

        self.assertEqual(entity.first("processingStatus"), self.manager.STATUS_SUCCESS)
