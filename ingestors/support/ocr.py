import time
import logging
import threading
from hashlib import sha1
from normality import stringify
from PIL import Image

from pyzbar import pyzbar
import numpy as np
import cv2

from io import BytesIO
from languagecodes import list_to_alpha3 as alpha3

from ingestors import settings
from ingestors.support.cache import CacheSupport
from ingestors.util import temp_locale

log = logging.getLogger(__name__)
TESSERACT_LOCALE = "C"


class OCRSupport(CacheSupport):
    MIN_SIZE = 1024 * 2
    MAX_SIZE = (1024 * 1024 * 30) - 1024

    def extract_ocr_text(self, data, languages=None):
        if not self.MIN_SIZE < len(data) < self.MAX_SIZE:
            log.info("OCR: file size out of range (%d)", len(data))
            return None

        languages = sorted(set(languages or []))
        data_key = sha1(data).hexdigest()
        key = self.cache_key("ocr", data_key, *languages)
        text = self.tags.get(key)
        if text is not None:
            log.info("OCR: %s chars cached", len(text))
            return stringify(text)

        if not hasattr(settings, "_ocr_service"):
            if settings.OCR_VISION_API:
                settings._ocr_service = GoogleOCRService()
            else:
                settings._ocr_service = LocalOCRService()

        text = settings._ocr_service.extract_text(data, languages=languages)
        if text is not None:
            self.tags.set(key, text)
            log.info("OCR: %s chars (from %s bytes)", len(text), len(data))
        return stringify(text)


class ZBarDetectorService(object):
    THRESHOLDS = list(range(32, 230, 32))

    def _enhance_image(self, image, threshold=127):
        width, height = image.size
        crop = (0, height - width * 3 / 2, width, height)
        # Convert to grayscale using Pillow
        gray_image = image.convert("L")

        # Convert Pillow image to OpenCV format
        opencv_image = np.array(gray_image)

        # Apply Gaussian blur to reduce noise
        blurred_image = cv2.GaussianBlur(opencv_image, (3, 3), 0)

        # Apply thresholding using OpenCV
        _, thresh_image = cv2.threshold(
            blurred_image, threshold, 255, cv2.THRESH_BINARY
        )

        # Apply morphological transformations to enhance the QR code
        kernel = np.ones((3, 3), np.uint8)
        dilated_image = cv2.dilate(thresh_image, kernel, iterations=1)
        eroded_image = cv2.erode(dilated_image, kernel, iterations=1)

        # Resize the image to make the QR code larger
        scale_percent = 200  # Adjust the scale as needed
        width = int(eroded_image.shape[1] * scale_percent / 100)
        height = int(eroded_image.shape[0] * scale_percent / 100)
        dim = (width, height)
        resized_image = cv2.resize(eroded_image, dim, interpolation=cv2.INTER_LINEAR)
        resized_image = cv2.GaussianBlur(eroded_image, (5, 5), 0)

        return Image.fromarray(resized_image)

    def _serialize_zbar_result(self, result):
        return "\n".join(
            [
                "",
                "--- CODE ---",
                "TYPE: {}".format(result.type),
                "QUALITY: {}".format(result.quality),
                "ORIENTATION: {}".format(result.orientation),
                "POSITION: {}".format(list(result.rect)),
                "DATA: {}".format(result.data.decode("utf-8")),
            ]
        )

    def _results_to_text(self, results):
        return "---\n".join([self._serialize_zbar_result(result) for result in results])

    def _try_best(self, image):
        results = pyzbar.decode(image)
        # Found it at first try
        if len(results) > 0:
            log.info("OCR: zbar found (%d) results at first shot", len(results))
            return results

        log.info("OCR: zbar ehnahcing image")
        # Try with our enhance logic
        for threshold in self.THRESHOLDS:
            log.info("OCR: zbar applying threshold %d", threshold)
            new_image = self._enhance_image(image, threshold=threshold)
            results = pyzbar.decode(new_image)

            if len(results) > 0:
                log.info(
                    "OCR: zbar found (%d) results with threshold=%d",
                    len(results),
                    threshold,
                )
                return results

        # no results found then
        return []

    def extract_barcodes(self, image):
        log.info("OCR: zbar scanning for codes")
        return self._results_to_text(self._try_best(image))


class LocalOCRService(object):
    """Perform OCR using an RPC-based service."""

    MAX_MODELS = 4

    def __init__(self):
        self.tl = threading.local()

    def language_list(self, languages):
        if not hasattr(settings, "ocr_supported"):
            with temp_locale(TESSERACT_LOCALE):
                # Tesseract language types:
                from tesserocr import get_languages

                _, settings.ocr_supported = get_languages()
                # log.info("OCR languages: %r", settings.ocr_supported)
        models = [c for c in alpha3(languages) if c in settings.ocr_supported]
        if len(models) > self.MAX_MODELS:
            log.warning("Too many models, limit: %s", self.MAX_MODELS)
            models = models[: self.MAX_MODELS]
        models.append("eng")
        return "+".join(sorted(set(models)))

    def configure_engine(self, languages):
        from tesserocr import PyTessBaseAPI, PSM, OEM

        if not hasattr(self.tl, "api") or self.tl.api is None:
            log.info("Configuring OCR engine (%s)", languages)
            self.tl.api = PyTessBaseAPI(
                lang=languages, oem=OEM.LSTM_ONLY, psm=PSM.AUTO_OSD
            )
        if languages != self.tl.api.GetInitLanguagesAsString():
            log.info("Re-initialising OCR engine (%s)", languages)
            self.tl.api.Init(lang=languages, oem=OEM.LSTM_ONLY)
        return self.tl.api

    def extract_text(self, data, languages=None):
        """Extract text from a binary string of data."""
        try:
            image = Image.open(BytesIO(data))
            image.load()
        except Exception as exc:
            log.error("Cannot open image data using Pillow: %s", exc)
            return ""

        text = ""
        with temp_locale(TESSERACT_LOCALE):
            languages = self.language_list(languages)
            api = self.configure_engine(languages)
            try:
                # TODO: play with contrast and sharpening the images.
                start_time = time.time()
                api.SetImage(image)
                text = api.GetUTF8Text()
                confidence = api.MeanTextConf()
                end_time = time.time()
                duration = end_time - start_time
                log.info(
                    "w: %s, h: %s, l: %s, c: %s, took: %.5f",
                    image.width,
                    image.height,
                    languages,
                    confidence,
                    duration,
                )
            except Exception as exc:
                log.error("OCR error: %s", exc)
            finally:
                api.Clear()

        text += ZBarDetectorService().extract_barcodes(image)
        return text


class GoogleOCRService(object):
    """Use Google's Vision API to perform OCR. This has very good quality
    but is quite expensive. For this reason, its use is controlled via a
    separate configuration variable, OCR_VISION_API, which must be set to
    'true'. To use the API, you must also have a service account JSON file
    under GOOGLE_APPLICATION_CREDENTIALS."""

    def __init__(self):
        import google.auth
        from google.cloud.vision import ImageAnnotatorClient

        credentials, project_id = google.auth.default()
        self.client = ImageAnnotatorClient(credentials=credentials)
        log.info("Using Google Vision API. Charges apply.")

    def extract_text(self, data, languages=None):
        try:
            from google.cloud.vision import types
        except ImportError:
            from google.cloud.vision_v1 import types

        image = types.Image(content=data)
        res = self.client.document_text_detection(image)
        return res.full_text_annotation.text or ""
