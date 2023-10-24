from .support import TestCase


class SevenZipArchivesTest(TestCase):
    def test_7z_archive(self):
        fixture_path, entity = self.fixture("500_pages.7z")
        self.manager.ingest(fixture_path, entity)

        self.assertEqual(entity.first("mimeType"), "application/x-7z-compressed")
        self.assertEqual(entity.first("processingStatus"), "success")

    def test_7z_archive_fragment(self):
        # the fixture file was archived and split into fragments
        # but only one of two fragments is present in the fixture dir
        fixture_path, entity = self.fixture("500_pages.7z.001")
        self.manager.ingest(fixture_path, entity)

        self.assertEqual(entity.first("mimeType"), "application/x-7z-compressed")
        self.assertEqual(entity.first("processingStatus"), "failure")
