try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
from PIL import Image
from PIL.Image import DecompressionBombError as DBE
from PIL.Image import DecompressionBombWarning as DBW

from ingestors.exc import ProcessingException


class ImageSupport(object):
    """Provides helpers for image extraction."""

    def parse_image(self, data):
        """Parse an image file into PIL."""
        try:
            image = Image.open(StringIO(data))
            image.load()
            return image
        except (DBE, DBW) as dce:
            raise ProcessingException("Image too large: %r" % dce)
        except IOError as ioe:
            raise ProcessingException("Unknown image format: %r" % ioe)
        except (RuntimeError, SyntaxError) as err:
            raise ProcessingException("Failed to load image: %r" % err)
