import logging

log = logging.getLogger(__name__)


class OCRSupport(object):
    """Provides helper for OCR tasks. Requires a Tesseract installation."""

    def extract_text_from_image(self, entity, data):
        """Extract text from a binary string of data."""
        languages = self.manager.ocr_languages
        languages.extend(entity.get('language'))
        return self.manager.ocr_service.extract_text(data, languages)
