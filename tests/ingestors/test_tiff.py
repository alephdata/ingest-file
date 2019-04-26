from ..support import TestCase


class TIFFIngestorTest(TestCase):

    def test_match(self):
        fixture_path, entity = self.fixture('multipage_tiff_example.tif')
        result = self.manager.ingest(fixture_path, entity)
        self.assertEqual(result.first('mimeType'), 'image/tiff')
        self.assertEqual(len(self.manager.entities), 11)
        self.assertEqual(
            result.first('processingStatus'), self.manager.STATUS_SUCCESS
        )

    def test_ingest_tiff_format(self):
        fixture_path, entity = self.fixture('hello_world_tiff.tif')
        result = self.manager.ingest(fixture_path, entity)

        self.assertEqual(self.manager.entities[0].first('bodyText'), 'HELLO WORLD')  # noqa
        self.assertEqual(
            result.first('processingStatus'), self.manager.STATUS_SUCCESS
        )
