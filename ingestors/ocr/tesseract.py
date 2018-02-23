import os
import logging
from threading import local
from banal import ensure_list
from tesserocr import PyTessBaseAPI, PSM  # noqa

from ingestors.ocr.languages import LANGUAGES

TESSDATA_PREFIX = '/usr/share/tesseract-ocr/'
TESSDATA_PREFIX = os.environ.get('TESSDATA_PREFIX', TESSDATA_PREFIX)

log = logging.getLogger(__name__)
thread = local()


def normalize_language(language):
    # tesserocr.get_languages()
    if language is None:
        return set()
    lang = language.lower().strip()
    matches = set()
    for (code, aliases) in LANGUAGES.items():
        if lang == code or lang in aliases:
            matches.add(code)
    return matches


def get_languages(codes, defaults):
    """Turn some ISO2 language codes into ISO3 codes."""
    languages = set([])
    for lang in ensure_list(codes):
        languages.update(normalize_language(lang))

    if not len(languages):
        for lang in defaults:
            languages.update(normalize_language(lang))

    languages.add('eng')
    return '+'.join(sorted(set(languages)))


def tesseract_image(self, image, languages, defaults):
    """Extract text from a binary string of data."""
    languages = get_languages(languages, defaults)

    if not hasattr(thread, 'api'):
        thread.api = PyTessBaseAPI(lang=languages,
                                   path=TESSDATA_PREFIX)
    else:
        thread.api.Init(path=TESSDATA_PREFIX, lang=languages)

    try:
        # TODO: play with contrast and sharpening the images.
        thread.api.SetPageSegMode(PSM.AUTO_OSD)
        thread.api.SetImage(image)
        return thread.api.GetUTF8Text()
    except RuntimeError as re:
        log.warning(re)
        return None
    finally:
        thread.api.Clear()
