import logging
from io import BytesIO
from PIL import Image
from threading import local
from abc import ABC, abstractmethod
from languagecodes import list_to_alpha3

log = logging.getLogger(__name__)


class OCRService(ABC):
    MAX_SIZE = (1024 * 1024 * 4) - 1024

    @classmethod
    def is_available(cls):
        return False

    @abstractmethod
    def extract_text(self, data, languages=None):
        pass


class LocalOCRService(OCRService):

    def __init__(self):
        self.thread = local()

    @classmethod
    def is_available(cls):
        try:
            from tesserocr import get_languages
            path, languages = get_languages()
            return len(languages) > 0
        except ImportError:
            return False

    def get_api(self, languages):
        if not hasattr(self.thread, 'api'):
            from tesserocr import PyTessBaseAPI, PSM
            api = PyTessBaseAPI(lang=languages)
            api.SetPageSegMode(PSM.AUTO_OSD)
            self.thread.api = api
        return self.thread.api

    def get_languages(self, languages):
        if not hasattr(self, 'supported_languages'):
            from tesserocr import get_languages
            _, self.supported_languages = get_languages()
        codes = set(['eng'])
        for lang in list_to_alpha3(codes):
            if lang in self.supported_languages:
                codes.add(lang)
        return '+'.join(sorted(codes))

    def extract_text(self, data, languages=None):
        """Extract text from a binary string of data."""
        languages = self.get_languages(languages)
        api = self.get_api(languages)

        if languages != api.GetInitLanguagesAsString():
            api.Init(lang=languages)

        try:
            # TODO: play with contrast and sharpening the images.
            image = Image.open(BytesIO(data))
            # if not self.image_size_ok(image):
            #     return
            api.SetImage(image)
            return api.GetUTF8Text()
        except Exception as ex:
            log.warning("Failed to OCR: %s", ex)
        finally:
            api.Clear()
