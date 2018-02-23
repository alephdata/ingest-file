import logging
from hashlib import sha1
from tesserocr import PyTessBaseAPI, PSM  # noqa

from ingestors.ocr.tesseract import tesseract_image
from ingestors.support.image import ImageSupport

log = logging.getLogger(__name__)


class OCRSupport(ImageSupport):
    """Provides helper for OCR tasks. Requires a Tesseract installation."""

    def extract_text_from_image(self, data, image=None):
        """Extract text from a binary string of data."""
        key = sha1(data).hexdigest()
        text = self.manager.get_cache(key)
        if text is not None:
            return text

        image = image or self.parse_image(data)
        defaults = self.manager.config.get('OCR_DEFAULTS', [])
        text = tesseract_image(image, self.result.languages, defaults)

        log.info('[%s] OCR: %s characters recognized', self.result, len(text))
        self.manager.set_cache(key, text)
        return text
