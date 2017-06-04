import os

from PIL import Image

from ingestors.ingestor import Ingestor
from ingestors.support.ocr import OCRSupport
from ingestors.support.fs import FSSupport


class ImageIngestor(Ingestor, FSSupport, OCRSupport):
    """Image file ingestor class.

    Extracts the text from images using OCR.

    Requires system tools:

    - convert
    - tesseract-ocr (including the tesseract data/language files)
    """

    MIME_TYPES = [
        'image/x-portable-graymap',
        'image/png',
        'image/tiff',
        'image/x-tiff',
        'image/jpeg',
        'image/bmp',
        'image/x-windows-bmp',
        'image/x-portable-bitmap',
        'application/postscript',
        'image/vnd.dxf',
        'image/svg+xml'
    ]

    MIN_WIDTH = 100
    MIN_HEIGHT = 100

    def configure(self):
        """Ingestor configuration."""
        config = super(ImageIngestor, self).configure()
        config['CONVERT_BIN'] = os.environ.get('CONVERT_BIN')
        config['LANGUAGES'] = os.environ.get('LANGUAGES') or 'eng'
        config['TESSDATA_PREFIX'] = (
            os.environ.get('TESSDATA_PREFIX') or '/usr/share/tesseract-ocr'
        )

        self.failure_exceptions += (IOError, Image.DecompressionBombWarning)

        return config

    def ingest(self, config):
        """Ingestor implementation.

        Converts the file to an image first. Next runs the OCR on it.
        """
        with self.create_temp_dir() as temp_dir:
            image_path = self.convert_to_image(
                self.file_path, config['CONVERT_BIN'], temp_dir
            )

            self.result.content = self.run_tesseract(image_path, config)
