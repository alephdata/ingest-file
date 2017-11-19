import logging
from hashlib import sha1
from banal import ensure_list
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO
from PIL import Image
from PIL.Image import DecompressionBombWarning
from tesserwrap import Tesseract, PageSegMode

from ingestors.support.ocr_languages import LANGUAGES

log = logging.getLogger(__name__)


class OCRSupport(object):
    """Provides helper for OCR tasks. Requires a Tesseract installation."""
    # https://tesserwrap.readthedocs.io/en/latest/#
    # https://pillow.readthedocs.io/en/3.0.x/reference/Image.html
    MIN_OCR_WIDTH = 100
    MIN_OCR_HEIGHT = 100

    def normalize_language(self, language):
        if language is None:
            return
        lang = language.lower().strip()
        matches = set()
        for (code, aliases) in LANGUAGES.items():
            if lang == code or lang in aliases:
                matches.add(code)
        return matches

    def get_languages(self, codes):
        """Turn (pre-set) ISO2 language codes into ISO3 codes."""
        languages = set([])
        for lang in ensure_list(codes):
            languages.update(self.normalize_language(lang))

        if not len(languages):
            for lang in self.manager.config.get('OCR_DEFAULTS', []):
                languages.update(self.normalize_language(lang))

        languages.add('eng')
        return '+'.join(sorted(set(languages)))

    def extract_text_from_image(self, data):
        """Extract text from a binary string of data."""
        tessdata = '/usr/share/tesseract-ocr'
        tessdata = self.manager.get_env('TESSDATA_PREFIX', tessdata)
        languages = self.get_languages(self.result.languages)

        key = sha1(data)
        key.update(languages)
        key = key.hexdigest()
        text = self.manager.get_cache(key)
        if text is not None:
            return text

        try:
            img = Image.open(StringIO(data))
        except DecompressionBombWarning as dce:
            log.warning("Image too large: %r", dce)
            return None
        except IOError as ioe:
            log.warning("Unknown image format: %r", ioe)
            return None
        if img.width < self.MIN_OCR_WIDTH and img.height < self.MIN_OCR_HEIGHT:
            log.warning("Image too small: %s", img.size)
            return None

        # TODO: play with contrast and sharpening the images.
        extractor = Tesseract(tessdata, lang=languages)
        extractor.set_image(img)
        extractor.set_page_seg_mode(PageSegMode.PSM_AUTO_OSD)
        text = extractor.get_text().strip()
        text = text.decode(encoding="utf-8")
        extractor.clear()

        log.debug('[%s] OCR: %s, %s characters extracted',
                  self.result, languages, len(text))
        self.manager.set_cache(key, text)
        return text
