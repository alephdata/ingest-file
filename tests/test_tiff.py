from .support import TestCase


class TIFFIngestorTest(TestCase):
    def test_match(self):
        fixture_path, entity = self.fixture("multipage_tiff_example.tif")
        self.manager.ingest(fixture_path, entity)

        emitted_image_entities = [
            x
            for x in self.get_emitted()
            if "mimeType" in x.properties and "image" in x.first("mimeType")
        ]

        # Have entities been emitted with a mime type that contains "image"?
        self.assertTrue(
            len(emitted_image_entities) != 0,
            f"Test failed for multipage_tiff_example.tif",
        )
        image_entity = emitted_image_entities.pop()

        self.assertEqual(image_entity.first("mimeType"), "image/tiff")
        self.assertEqual(
            image_entity.first("processingStatus"), self.manager.STATUS_SUCCESS
        )
        entities = self.get_emitted()
        self.assertEqual(len(entities), 11)

    def test_ingest_tiff_format(self):
        fixture_path, entity = self.fixture("hello_world_tiff.tif")
        self.manager.ingest(fixture_path, entity)

        emitted_image_entities = [
            x
            for x in self.get_emitted()
            if "mimeType" in x.properties and "image" in x.first("mimeType")
        ]

        # Have entities been emitted with a mime type that contains "image"?
        self.assertTrue(
            len(emitted_image_entities) != 0,
            f"Test failed for multipage_tiff_example.tif",
        )
        image_entity = emitted_image_entities.pop()

        self.assertEqual(
            image_entity.first("processingStatus"), self.manager.STATUS_SUCCESS
        )
        self.assertEqual(image_entity.first("indexText"), "HELLO WORLD")
