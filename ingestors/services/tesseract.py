import os
import logging
from io import BytesIO
from PIL import Image
from threading import local
from languagecodes import list_to_alpha3
from tesserocr import get_languages, PyTessBaseAPI, PSM  # noqa

from ingestors.services.interfaces import OCRService
from ingestors.services.util import OCRUtils

log = logging.getLogger(__name__)


class TesseractService(OCRService, OCRUtils):

    def __init__(self, prefix=None):
        self.prefix = '/usr/share/tesseract-ocr/'
        self.prefix = os.environ.get('TESSDATA_PREFIX', self.prefix)
        self.prefix = prefix or self.prefix
        self.thread = local()
        _, self.supported_languages = get_languages()

    def get_api(self, languages):
        if not hasattr(self.thread, 'api'):
            api = PyTessBaseAPI(path=self.prefix, lang=languages)
            api.SetPageSegMode(PSM.AUTO_OSD)
            self.thread.api = api
        return self.thread.api

    def extract_text(self, data, languages=None):
        """Extract text from a binary string of data."""
        codes = set(['eng'])
        for lang in list_to_alpha3(codes):
            if lang in self.supported_languages:
                codes.add(lang)
        languages = '+'.join(sorted(codes))
        api = self.get_api(languages)

        if languages != api.GetInitLanguagesAsString():
            api.Init(path=self.prefix, lang=languages)

        try:
            # TODO: play with contrast and sharpening the images.
            image = Image.open(BytesIO(data))
            if not self.image_size_ok(image):
                return
            api.SetImage(image)
            return api.GetUTF8Text()
        except Exception as ex:
            log.warning("Failed to OCR: %s", ex)
        finally:
            api.Clear()
