from ingestors import Result
from ..support import TestCase


class TIFFIngestorTest(TestCase):

    def test_match(self):
        fixture_path = self.fixture('multipage_tiff_example.tif')
        result = self.manager.ingest(fixture_path)
        self.assertEqual(result.mime_type, 'image/tiff')
        self.assertEqual(len(result.pages), 10)
        self.assertEqual(result.status, Result.STATUS_SUCCESS)

    def test_ingest_tiff_format(self):
        fixture_path = self.fixture('hello_world_tiff.tif')
        result = self.manager.ingest(fixture_path)

        self.assertEqual(result.pages[0]['text'], 'HELLO WORLD')
        self.assertEqual(result.status, Result.STATUS_SUCCESS)
