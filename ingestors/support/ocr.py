import os.path
import logging
import subprocess
from distutils.spawn import find_executable

try:
    from PIL import Image
    from tesserwrap import Tesseract, PageSegMode
except ImportError as error:
    logging.exception(error)


class OCRSupport(object):
    """Provides helper for OCR tasks.

    Requires a Tesseract installation.
    """

    logger = logging.getLogger(__name__)

    def convert_to_image(self, file_path, convert_bin, temp_dir):
        """Converts a file to an image."""
        out_path = os.path.join(temp_dir, 'converted.jpg')
        convert_bin = convert_bin or find_executable('convert')

        if not convert_bin:
            raise RuntimeError('No image convertion tools available.')

        convert = [
            convert_bin,
            file_path,
            '-density', '450',
            '-define', 'pdf:fit-page=A4',
            out_path
        ]
        subprocess.call(convert)

        assert os.path.isfile(out_path), 'Conversion failed.'

        return out_path

    def run_tesseract(self, file_path, config):
        """Extract text from a binary string of data."""
        if not config['TESSDATA_PREFIX']:
            raise RuntimeError('No TESSDATA_PREFIX available.')

        img = Image.open(file_path)

        small = (img.width < self.MIN_WIDTH and img.height < self.MIN_HEIGHT)
        assert small is False, 'Image size too small: {}'.format(img.size)

        # TODO: play with contrast and sharpening the images.
        extractor = Tesseract(
            config['TESSDATA_PREFIX'], lang=config['LANGUAGES']
        )
        extractor.set_image(img)
        extractor.set_page_seg_mode(PageSegMode.PSM_AUTO_OSD)
        text = extractor.get_text().strip()
        extractor.clear()

        self.logger.debug(
            'OCR extracted: %s characters. Languages used: %r',
            len(text), config['LANGUAGES']
        )

        return text or None
