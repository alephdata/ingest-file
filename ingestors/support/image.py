from io import BytesIO
from PIL import Image

from ingestors.exc import ProcessingException


class ImageSupport(object):
    """Provides helpers for image extraction."""

    def parse_image(self, data):
        """Parse an image file into PIL."""
        try:
            image = Image.open(BytesIO(data))
            image.load()
            return image
        except Exception as err:
            raise ProcessingException("Failed to load image: %r" % err)
