try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
from PIL import Image
from PIL.Image import DecompressionBombWarning

from ingestors.exc import ProcessingException


class ImageSupport(object):
    """Provides helpers for image extraction."""

    def parse_image(self, data):
        """Parse an image file into PIL."""
        try:
            image = Image.open(StringIO(data))
            image.load()
            return image
        except DecompressionBombWarning as dce:
            raise ProcessingException("Image too large: %r" % dce)
        except IOError as ioe:
            raise ProcessingException("Unknown image format: %r" % ioe)
        except RuntimeError as err:
            raise ProcessingException("Failed to load image: %r" % err)
