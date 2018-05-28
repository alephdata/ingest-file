import os
import logging
from io import BytesIO
from PIL import Image
from threading import local
from banal import ensure_list
from tesserocr import PyTessBaseAPI, PSM  # noqa
from PIL.Image import DecompressionBombError as DBE
from PIL.Image import DecompressionBombWarning as DBW

from ingestors.services.interfaces import OCRService

log = logging.getLogger(__name__)


class TesseractService(OCRService):
    # Tesseract 3.05 language types:
    LANGUAGES = {
        'afr': ['af'],
        'amh': ['am'],
        'ara': ['ar'],  # arabic
        'asm': ['as'],
        'aze': ['az'],
        'aze_cyrl': ['az', 'aze'],
        'bel': ['be'],
        'ben': ['bn'],
        'bod': ['tib', 'bo'],
        'bos': ['bs', 'hbs'],
        'bul': ['bg'],
        'cat': ['ca'],
        'ceb': [],
        'ces': ['cze', 's'],
        'chi_sim': ['chi', 'zho', 'zh'],
        'chi_tra': ['chi', 'zho', 'zh'],
        'chr': [],
        'cym': ['wel', 'cy'],
        'deu': ['ger', 'de'],
        'dzo': ['dz'],
        'ell': ['gre', 'el'],
        'eng': ['en', 'enm'],
        'enm': [],  # middle en
        'epo': ['eo'],
        'equ': [''],
        'est': ['et'],
        'eus': ['baq', 'eu'],
        'fas': ['per', 'fa'],
        'fin': ['fi'],
        'fra': ['fre', 'fr', 'frm'],
        'frk': [],  # fraktur
        'frm': [],  # middle french
        'gle': ['ga'],
        'glg': ['gl'],
        'grc': [],  # classic el
        'guj': ['gu'],
        'hat': ['ht'],
        'heb': ['he'],
        'hin': ['hi'],
        'hrv': ['hr', 'hbs'],
        'hun': ['hu'],
        'iku': ['iu'],  # inuktitut
        'isl': ['ice', 'is'],
        'ita': ['it'],
        'jav': ['jv'],
        'jpn': ['ja'],
        'kan': ['kn'],  # kannada
        'kat': ['geo', 'ka'],
        'kaz': ['kk'],
        'khm': ['km'],
        'kir': ['ky'],
        'kor': ['ko'],
        'kur': ['ku'],
        'lao': ['lo'],
        'lat': ['la'],
        'lav': ['lv'],
        'lit': ['lt'],
        'mal': ['ml'],
        'mar': ['mr'],
        'mkd': ['mk', 'mac'],
        'mlt': ['mt'],
        'msa': ['may', 'ms'],
        'mya': ['bur', 'my'],
        'nep': ['ne'],
        'nld': ['dut', 'nl'],
        'nor': ['no', 'non'],
        'ori': ['or'],
        'pan': ['pa'],
        'pol': ['pl'],
        'por': ['pt'],
        'pus': ['ps'],
        'ron': ['rum', 'ro'],
        'rus': ['ru'],
        'san': ['sa'],
        'sin': ['si'],
        'slk': ['slo', 'sk'],
        'slv': ['sl'],
        'spa': ['es'],
        'sqi': ['alb', 'sq'],
        'srp': ['sr', 'hbs'],
        'swa': ['sw'],
        'swe': ['sv'],
        'syr': [],
        'tam': ['ta'],
        'tel': ['te'],
        'tgk': ['tg'],
        'tgl': ['tl'],
        'tha': ['th'],
        'tir': ['ti'],
        'tur': ['tr'],
        'uig': ['ug'],
        'ukr': ['uk'],
        'urd': ['ur'],
        'uzb': ['uz'],
        'vie': ['vi'],
        'yid': ['yi']
    }

    def __init__(self, prefix=None):
        self.prefix = '/usr/share/tesseract-ocr/'
        self.prefix = os.environ.get('TESSDATA_PREFIX', self.prefix)
        self.prefix = prefix or self.prefix
        self.thread = local()

    def normalize_language(self, language):
        """Turn some ISO2 language codes into ISO3 codes."""
        # tesserocr.get_languages()
        if language is None:
            return set()
        lang = language.lower().strip()
        matches = set()
        for (code, aliases) in self.LANGUAGES.items():
            if lang == code or lang in aliases:
                matches.add(code)
        return matches

    def get_api(self, languages):
        if not hasattr(self.thread, 'api'):
            api = PyTessBaseAPI(path=self.prefix, lang=languages)
            api.SetPageSegMode(PSM.AUTO_OSD)
            self.thread.api = api
        return self.thread.api

    def extract_text(self, data, languages=None):
        """Extract text from a binary string of data."""
        codes = set(['eng'])
        for lang in ensure_list(codes):
            codes.update(self.normalize_language(lang))
        languages = '+'.join(sorted(codes))
        api = self.get_api(languages)

        if languages != api.GetInitLanguagesAsString():
            api.Init(path=self.prefix, lang=languages)

        try:
            # TODO: play with contrast and sharpening the images.
            image = Image.open(BytesIO(data))
            api.SetImage(image)
            return api.GetUTF8Text()
        except (DBE, DBW, IOError, RuntimeError, SyntaxError) as re:
            log.exception("Failed to OCR: %s", languages)
            return None
        finally:
            api.Clear()
