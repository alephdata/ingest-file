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

    def test_tesseract_ocr_regression(self):
        """This test is meant to catch a regression in the OCR behaviour
        described in this PR: https://github.com/alephdata/ingest-file/pull/585"""

        test_data = {
            "jpeg": {
                "file": "regression_jpg.jpg",
                "content": "Debian -- Packages",
                "mime_type": "image/jpeg",
            },
            "gif": {
                "file": "regression_gif.gif",
                "content": "This is text inside a GIF image",
                "mime_type": "image/gif",
            },
            "tiff": {
                "file": "regression_tiff.tiff",
                "content": "Debian -- Packages",
                "mime_type": "image/tiff",
            },
            "webp": {
                "file": "regression_webp.webp",
                "content": "Debian -- Packages",
                "mime_type": "image/webp",
            },
            "openjpeg": {
                "file": "regression_openjpeg.jp2",
                "content": "Debian -- Packages",
                "mime_type": "image/jp2",
            },
        }

        for test_image_type in test_data:
            fixture_path, entity = self.fixture(test_data[test_image_type]["file"])
            self.manager.ingest(fixture_path, entity)

            emitted_image_entities = [
                x
                for x in self.get_emitted()
                if "mimeType" in x.properties and "image" in x.first("mimeType")
            ]

            # Have entities been emitted with a mime type that contains "image"?
            self.assertTrue(
                len(emitted_image_entities) != 0,
                f"Test failed for {test_data[test_image_type]['file']}",
            )
            image_entity = emitted_image_entities.pop()

            # Is the mimeType correct?
            self.assertEqual(
                image_entity.first("mimeType"),
                test_data[test_image_type]["mime_type"],
                f"Test failed for {test_data[test_image_type]['file']}",
            )

            # Is the processing status of the entity == SUCCESS?
            self.assertEqual(
                image_entity.first("processingStatus"),
                self.manager.STATUS_SUCCESS,
                f"Test failed for {test_data[test_image_type]['file']}",
            )

            # Does either the bodyText prop or the indexText prop contain
            # the text resulted from OCR?
            try:
                self.assertIn(
                    test_data[test_image_type]["content"],
                    image_entity.first("bodyText"),
                    f"Test failed for {test_data[test_image_type]['file']}",
                )
            except TypeError:
                self.assertIn(
                    test_data[test_image_type]["content"],
                    image_entity.first("indexText"),
                    f"Test failed for {test_data[test_image_type]['file']}",
                )

    def test_ingest_heif(self):
        fixture_path, entity = self.fixture("image1.heic")
        self.manager.ingest(fixture_path, entity)

        self.assertEqual(
            entity.first("processingStatus"),
            self.manager.STATUS_SUCCESS,
        )
