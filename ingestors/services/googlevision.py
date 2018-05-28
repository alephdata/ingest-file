# https://googlecloudplatform.github.io/google-cloud-python/latest/vision/index.html
import logging
import google.auth
from google.auth import exceptions
from google.cloud.vision import ImageAnnotatorClient
from google.cloud.vision import types

from ingestors.services.interfaces import OCRService

log = logging.getLogger(__name__)


class GoogleVisionService(OCRService):

    def __init__(self):
        credentials, project_id = google.auth.default()
        try:
            self.client = ImageAnnotatorClient(credentials=credentials)
            log.info("Using Google Vision API. Charges apply.")
        except exceptions.DefaultCredentialsError:
            log.error("Google Platform credentials not set, disabling Vision API.")  # noqa
            self.client = None

    def check_available(self):
        return self.client is not None

    def extract_text_from_image(self, data, languages=None):
        # TODO: downsample very large images, or make them
        # grayscale before sending into gRPC.
        image = types.Image(content=data)
        res = self.client.document_text_detection(image)
        ann = res.full_text_annotation
        return ann.text
