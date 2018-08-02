import logging

log = logging.getLogger(__name__)


class OCRSupport(object):
    """Provides helper for OCR tasks. Requires a Tesseract installation."""

    def extract_text_from_image(self, data):
        """Extract text from a binary string of data."""
        languages = self.result.ocr_languages
        text = self.manager.ocr_service.extract_text(data, languages)
        return text
