import logging
from hashlib import sha1
from banal import ensure_list
from tesserocr import PyTessBaseAPI

from ingestors.support.ocr_languages import LANGUAGES
from ingestors.support.image import ImageSupport
from ingestors.exc import ProcessingException

log = logging.getLogger(__name__)


class OCRSupport(ImageSupport):
    """Provides helper for OCR tasks. Requires a Tesseract installation."""
    # https://tesserwrap.readthedocs.io/en/latest/#
    # https://pillow.readthedocs.io/en/3.0.x/reference/Image.html

    def normalize_language(self, language):
        # tesserocr.get_languages()
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

    def extract_text_from_image(self, data, image=None):
        """Extract text from a binary string of data."""
        tessdata = '/usr/share/tesseract-ocr/'
        tessdata = self.manager.get_env('TESSDATA_PREFIX', tessdata)
        languages = self.get_languages(self.result.languages)

        key = sha1(data)
        key.update(languages)
        key = key.hexdigest()
        text = self.manager.get_cache(key)
        if text is not None:
            return text

        api = PyTessBaseAPI(lang=languages, path=tessdata)
        try:
            image = image or self.parse_image(data)
            # TODO: play with contrast and sharpening the images.
            api.SetImage(image)
            text = api.GetUTF8Text()
        except ProcessingException as pe:
            log.warning(pe)
            return None
        finally:
            api.Clear()

        log.info('[%s] OCR: %s, %s characters extracted',
                 self.result, languages, len(text))
        self.manager.set_cache(key, text)
        return text
