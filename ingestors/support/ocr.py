import logging
from hashlib import sha1

log = logging.getLogger(__name__)


class OCRSupport(object):
    """Provides helper for OCR tasks. Requires a Tesseract installation."""

    def extract_text_from_image(self, data):
        """Extract text from a binary string of data."""
        key = sha1(data).hexdigest()
        text = self.manager.get_cache(key)
        if text is not None:
            if len(text):
                log.info('[%s] OCR: %s chars cached', self.result, len(text))
            return text

        languages = self.result.ocr_languages
        text = self.manager.ocr_service.extract_text(data, languages)
        if text is None:
            return

        if len(text):
            log.info('[%s] OCR: %s chars recognized', self.result, len(text))
        self.manager.set_cache(key, text)
        return text
