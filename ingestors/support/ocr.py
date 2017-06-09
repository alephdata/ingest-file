import logging
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO
from PIL import Image
from PIL.Image import DecompressionBombWarning
from pycountry import languages
from tesserwrap import Tesseract, PageSegMode

log = logging.getLogger(__name__)


class OCRSupport(object):
    """Provides helper for OCR tasks. Requires a Tesseract installation."""
    # https://tesserwrap.readthedocs.io/en/latest/#
    # https://pillow.readthedocs.io/en/3.0.x/reference/Image.html
    MIN_OCR_WIDTH = 100
    MIN_OCR_HEIGHT = 100

    def convert_iso_languages(self, codes):
        """Turn (pre-set) ISO2 language codes into ISO3 codes."""
        supported = []
        if not isinstance(codes, (list, set, tuple)):
            codes = [codes]
        for lang in codes:
            if lang is None:
                continue
            lang = lang.lower().strip()
            if lang is None or len(lang) not in [2, 3]:
                continue
            if len(lang) == 2:
                try:
                    c = languages.get(alpha_2=lang)
                    lang = c.alpha_3.lower()
                except KeyError:
                    log.warning("Invalid language code: %s", lang)
                    continue
            supported.append(lang)

        # if not len(supported):
        supported.append('eng')
        return '+'.join(sorted(set(supported)))

    def extract_text_from_image(self, data):
        """Extract text from a binary string of data."""
        tessdata = self.manager.get_env('TESSDATA_PREFIX', '/usr/share/tesseract-ocr')  # noqa

        languages = self.result.languages or \
            self.manager.config.get('LANGUAGES', ['en'])
        languages = self.convert_iso_languages(languages)

        # text = Cache.get_ocr(data, languages)
        # if text is not None:
        #    return text
        try:
            img = Image.open(StringIO(data))
        except DecompressionBombWarning as dce:
            log.warning("Image too large: %", dce)
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
        text = text.decode(encoding="UTF-8")
        extractor.clear()

        log.debug('[%s] OCR: %s, %s characters extracted',
                  self.result.label, languages, len(text))
        # Cache.set_ocr(data, languages, text)
        return text
