import os.path
import logging
import subprocess32 as subprocess
from urlparse import urljoin
from distutils.spawn import find_executable

import urllib3
from normality import stringify


class PDFSupport(object):
    """Provides support for extracting data from PDF.

    Can use a TIKA server or Poppler system tools.
    """

    logger = logging.getLogger(__name__)

    #: Poppler tools XML selector for page breaks
    POPPLER_PAGE_SELECTOR = './page'
    #: TIKA response XML selector for page breaks
    TIKA_PAGE_SELECTOR = './/div[@class="page"]'

    def pdf_to_xml(self, fio, file_path, temp_dir, config):
        """Converts a PDF to XML using any of the available tools."""
        if config.get('TIKA_URI'):
            return self.pdf_to_xml_tika(fio, config['TIKA_URI'], temp_dir)
        elif config.get('PDFTOHTML_BIN'):
            return self.pdf_to_xml_poppler(
                file_path, config['PDFTOHTML_BIN'], temp_dir)
        elif find_executable('pdftohtml'):
            return self.pdf_to_xml_poppler(
                file_path, find_executable('pdftohtml'), temp_dir)
        else:
            raise RuntimeError('No PDF extraction tools available.')

    def pdf_to_xml_poppler(self, file_path, bin_path, temp_dir):
        out_file = os.path.join(temp_dir, 'pdf.xml')
        self.logger.info(
            'Converting %r using %r...', file_path, bin_path)

        pdftohtml = [
            bin_path,
            '-xml',
            '-hidden',
            '-q',
            '-nodrm',
            file_path,
            out_file
        ]

        retcode = subprocess.call(pdftohtml)
        assert retcode == 0, 'Execution failed: {}'.format(pdftohtml)
        assert os.path.exists(out_file), 'File missing: {}'.format(out_file)

        with open(out_file, 'r') as htmlio:
            xml = stringify(htmlio.read())
            xml = xml.replace('encoding="UTF-8"', '')

            self.logger.debug('Extracted XML from: %r', file_path)

            return xml, self.POPPLER_PAGE_SELECTOR

    def pdf_to_xml_tika(self, fio, tika_url, temp_dir):
        tika_url = urljoin(tika_url, '/tika')
        http = urllib3.PoolManager()

        response = http.request(
            'PUT',
            tika_url,
            body=fio.read(),
            headers={
                'Accept': 'text/html',
                'Content-Type': 'application/pdf'
            }
        )

        xml = response.data.decode('utf-8')
        response.close()
        http.clear()

        return xml, self.TIKA_PAGE_SELECTOR

    def pdf_page_to_image(self, pagenum, file_path, bin_path, temp_dir):
        """Extract a page as an image and perform OCR.

        Used mainly because pdftohtml generated images could be really bad,
        e.g. inverted colors and weird rotations in TIFF files.
        A better idea is to make an image out of the whole page and OCR it.
        """
        bin_path = bin_path or find_executable('pdftoppm')
        out_path = os.path.join(temp_dir, '{}.pgm'.format(pagenum))

        # TODO: figure out if there's something nicer than 300dpi. Seems
        # like tesseract is trained on 300 and 600 actually sometimes gives
        # worse results.
        pdftoppm = [
            bin_path,
            '-f', pagenum,
            '-singlefile',
            '-r', '300',
            '-gray',
            file_path,
            out_path.replace('.pgm', '')
        ]

        retcode = subprocess.call(pdftoppm)
        assert retcode == 0, 'Execution failed: {}'.format(pdftoppm)
        assert os.path.exists(out_path), 'File missing: {}'.format(out_path)

        self.logger.debug(
            'Extracted PDF page %r to image from: %r', pagenum, out_path)

        return out_path
