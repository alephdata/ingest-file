import logging

# https://googlecloudplatform.github.io/google-cloud-python/latest/vision/index.html
import google.auth
from google.auth import exceptions
from google.cloud.vision import ImageAnnotatorClient
from google.cloud.vision import types

log = logging.getLogger(__name__)
client = {}


def _vision_client():
    if '_' not in client:
        try:
            credentials, project_id = google.auth.default()
            client['_'] = ImageAnnotatorClient(credentials=credentials)
            log.info("Using Google Vision API. Charges apply.")
        except exceptions.DefaultCredentialsError:
            log.info("Google Platform credentials not set, disabling Vision API.")
            client['_'] = None
    return client['_']


def vision_available():
    """Check if Google Vision API is configured and available."""
    return _vision_client() is not None


def vision_data(data):
    client = _vision_client()
    if client is None:
        log.warning("Called Vision API without configuration.")
        return

    image = types.Image(content=data)
    res = client.document_text_detection(image)
    ann = res.full_text_annotation
    return ann.text
