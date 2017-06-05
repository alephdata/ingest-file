import os
from PIL import Image
from PIL.Image import DecompressionBombWarning

from ingestors.base import Ingestor
from ingestors.support.pdf import PDFSupport
from ingestors.exc import ProcessingException


class ImageIngestor(Ingestor, PDFSupport):
    """Image file ingestor class.

    Extracts the text from images using OCR.
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

    def check_image_size(self, local_path):
        if self.result.mime_type in ['image/svg+xml']:
            return
        try:
            with open(local_path, 'r') as fh:
                img = Image.open(fh)
                if img.width < self.MIN_WIDTH or img.height < self.MIN_HEIGHT:
                    raise ProcessingException("Image too small: %s", img.size)
                return True
        except DecompressionBombWarning as dce:
            raise ProcessingException("Image too large: %s", dce)
        except Exception as exc:
            raise ProcessingException("Cannot open image: %s", exc)

    def ingest(self, file_path):
        with self.create_temp_dir() as temp_dir:
            pdf_path = os.path.join(temp_dir, 'image.pdf')
            self.check_image_size(file_path)
            self.exec_command('convert',
                              file_path,
                              '-density', '450',
                              '-define',
                              'pdf:fit-page=A4',
                              pdf_path)
            self.assert_outfile(pdf_path)
            self.pdf_alternative_extract(pdf_path)
