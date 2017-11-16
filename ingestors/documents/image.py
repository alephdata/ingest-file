from datetime import datetime
from PIL import Image, ExifTags
from PIL.Image import DecompressionBombWarning

from ingestors.base import Ingestor
from ingestors.support.pdf import PDFSupport
from ingestors.exc import ProcessingException
from ingestors.util import join_path


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
        'image/gif',
        'image/pjpeg',
        'image/bmp',
        'image/x-windows-bmp',
        'image/x-portable-bitmap',
        'application/postscript',
        'image/vnd.dxf',
    ]
    EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'bmp']
    SCORE = 5

    MIN_WIDTH = 100
    MIN_HEIGHT = 100

    def parse_exif_date(self, date):
        try:
            return datetime.strptime(date, '%Y:%m:%d %H:%M:%S')
        except ValueError:
            return None

    def extract_exif(self, img):
        if not hasattr(img, '_getexif'):
            return

        exif = img._getexif()
        if exif is None:
            return            

        make, model = '', ''
        for num, value in exif.items():
            tag = ExifTags.TAGS[num]
            if tag == 'DateTimeOriginal':
                if not self.result.created_at:
                    self.result.created_at = self.parse_exif_date(value)
            if tag == 'DateTime':
                if not self.result.date:
                    self.result.date = self.parse_exif_date(value)
            if tag == 'Make':
                make = value
            if tag == 'Model':
                model = value

        generator = ' '.join((make, model))
        self.result.generator = generator.strip()

    def ingest(self, file_path):
        with open(file_path, 'r') as fh:
            try:
                img = Image.open(fh)
            except DecompressionBombWarning as dce:
                raise ProcessingException("Image too large: %s", dce)
            except IOError as ioe:
                raise ProcessingException("Cannot open image: %s", ioe)

        self.extract_exif(img)

        if img.width >= self.MIN_WIDTH and img.height >= self.MIN_HEIGHT:
            with self.create_temp_dir() as temp_dir:
                pdf_path = join_path(temp_dir, 'image.pdf')
                self.exec_command('convert',
                                  file_path,
                                  '-density', '300',
                                  '-define',
                                  'pdf:fit-page=A4',
                                  pdf_path)
                self.assert_outfile(pdf_path)
                self.pdf_alternative_extract(pdf_path)


class SVGIngestor(Ingestor, PDFSupport):
    MIME_TYPES = [
        'image/svg+xml'
    ]
    EXTENSIONS = ['svg']
    SCORE = 20

    def ingest(self, file_path):
        with self.create_temp_dir() as temp_dir:
            pdf_path = join_path(temp_dir, 'image.pdf')
            self.exec_command('convert',
                              file_path,
                              '-density', '300',
                              '-define',
                              'pdf:fit-page=A4',
                              pdf_path)
            self.assert_outfile(pdf_path)
            self.pdf_alternative_extract(pdf_path)
