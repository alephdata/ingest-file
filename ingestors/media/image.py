import logging
from PIL import ExifTags
from datetime import datetime
from followthemoney import model

from ingestors.services import get_ocr
from ingestors.ingestor import Ingestor
from ingestors.support.image import ImageSupport
from ingestors.support.plain import PlainTextSupport

log = logging.getLogger(__name__)


class ImageIngestor(Ingestor, ImageSupport, PlainTextSupport):
    """Image file ingestor class.

    Extracts the text from images using OCR.
    """

    MIME_TYPES = [
        'image/x-portable-graymap',
        'image/png',
        'image/x-png',
        'image/jpeg',
        'image/jpg',
        'image/gif',
        'image/pjpeg',
        'image/bmp',
        'image/x-windows-bmp',
        'image/x-portable-bitmap',
        'image/x-coreldraw',
        'application/postscript',
        'image/vnd.dxf',
    ]
    EXTENSIONS = [
        'jpg',
        'jpeg',
        'png',
        'gif',
        'bmp'
    ]
    SCORE = 10

    def parse_exif_date(self, date):
        try:
            return datetime.strptime(date, '%Y:%m:%d %H:%M:%S')
        except Exception:
            return None

    def extract_exif(self, img):
        if not hasattr(img, '_getexif'):
            return

        exif = img._getexif()
        if exif is None:
            return

        make, model = '', ''
        for num, value in exif.items():
            try:
                tag = ExifTags.TAGS[num]
            except KeyError:
                log.warning("Unknown EXIF code: %s", num)
                continue
            if tag == 'DateTimeOriginal':
                self.update('created_at', self.parse_exif_date(value))
            if tag == 'DateTime':
                self.update('date', self.parse_exif_date(value))
            if tag == 'Make':
                make = value
            if tag == 'Model':
                model = value

        generator = ' '.join((make, model))
        self.update('generator', generator.strip())

    def ingest(self, file_path, entity):
        entity.schema = model.get('Image')
        with open(file_path, 'rb') as fh:
            data = fh.read()

        image = self.parse_image(data)
        self.extract_exif(image)

        ocr = get_ocr()
        text = ocr.extract_text(data, languages=self.result.ocr_languages)
        self.extract_plain_text_content(text)

    @classmethod
    def match(cls, file_path, entity):
        score = super(ImageIngestor, cls).match(file_path, entity)
        if score <= 0:
            for mime_type in entity.get('mimeType'):
                if mime_type.startswith('image/'):
                    score = cls.SCORE - 1
        return score
