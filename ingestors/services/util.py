import logging
from PIL import Image
from io import BytesIO

log = logging.getLogger(__name__)


class OCRUtils(object):
    MAX_SIZE = (1024 * 1024 * 4) - 1024
    MIN_WIDTH = 10
    MIN_HEIGHT = 10

    def image_size_ok(self, image):
        if image.width <= self.MIN_WIDTH:
            return False
        if image.height <= self.MIN_HEIGHT:
            return False
        return True

    def ensure_size(self, data):
        """This is a utility to scale images submitted to OCR such that
        they will fit into the body of a gRPC message, used both by
        Google's Vision API and by Aleph's recognize-text microservice.
        This is primarily because gRPC has a built-in limit, but it also seems
        like good practice independently - reformatting broken image formats
        into clean PNGs before doing OCR."""
        if len(data) < self.MAX_SIZE:
            return data

        try:
            image = Image.open(BytesIO(data))
            image.load()
            factor = 1.0
            while True:
                size = (int(image.width * factor), int(image.height * factor))
                resized = image.resize(size, Image.ANTIALIAS)
                if not self.image_size_ok(image):
                    return

                with BytesIO() as output:
                    resized.save(output, format='png')
                    png_data = output.getvalue()

                # log.warn("Size: %s, %s", len(data), len(png_data))
                if len(png_data) < self.MAX_SIZE:
                    return png_data
                factor *= 0.9
        except Exception as err:
            log.exception("Cannot open image for OCR.")
