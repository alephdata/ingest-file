import io
from unittest import skipUnless

from ingestors.image import ImageIngestor

from ..support import TestCase


class ImageIngestorTest(TestCase):

    def test_ingest_on_svg(self):
        fixture_path = self.fixture('image.svg')

        with io.open(fixture_path, mode='rb') as fio:
            ing = ImageIngestor(fio, fixture_path)
            ing.run()

        self.assertEqual(ing.result.content, u'Testing ingestors 1..2..3..')
        self.assertEqual(ing.status, ImageIngestor.STATUSES.SUCCESS)
        self.assertEqual(ing.state, ImageIngestor.STATES.FINISHED)

    @skipUnless(TestCase.EXTRA_FIXTURES, 'No extra fixtures.')
    def test_ingest_hand_written_text(self):
        fixture_path = self.fixture('images/some hand wirtten veird text.jpg')

        with io.open(fixture_path, mode='rb') as fio:
            ing = ImageIngestor(fio, fixture_path)
            ing.run()

        self.assertIsNone(ing.result.content)
        self.assertEqual(ing.status, ImageIngestor.STATUSES.SUCCESS)
        self.assertEqual(ing.state, ImageIngestor.STATES.FINISHED)

    @skipUnless(TestCase.EXTRA_FIXTURES, 'No extra fixtures.')
    def test_ingest_tiff_format(self):
        fixture_path = self.fixture('formats/image/hello_world_tiff.tif')

        with io.open(fixture_path, mode='rb') as fio:
            ing = ImageIngestor(fio, fixture_path)
            ing.run()

        self.assertEqual(ing.result.content, 'HELLO WORLD')
        self.assertEqual(ing.status, ImageIngestor.STATUSES.SUCCESS)
        self.assertEqual(ing.state, ImageIngestor.STATES.FINISHED)

    @skipUnless(TestCase.EXTRA_FIXTURES, 'No extra fixtures.')
    def test_ingest_too_small(self):
        fixture_path = self.fixture('formats/image/1_black_pixel.png')

        with io.open(fixture_path, mode='rb') as fio:
            ing = ImageIngestor(fio, fixture_path)
            ing.run()

        self.assertIsNone(ing.result.content)
        self.assertEqual(ing.status, ImageIngestor.STATUSES.FAILURE)
        self.assertEqual(ing.state, ImageIngestor.STATES.FINISHED)
