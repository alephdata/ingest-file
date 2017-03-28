import os.path
import subprocess
from distutils.spawn import find_executable
from logging import getLogger
from urlparse import urljoin

import urllib3
from normality import stringify


class PDFSupport(object):
    """Provides support for extracting data from PDF."""

    logger = getLogger(__name__)

    #: Poppler tools XML selector for page breaks
    POPPLER_PAGE_SELECTOR = './page'
    #: TIKA response XML selector for page breaks
    TIKA_PAGE_SELECTOR = './/div[@class="page"]'

    def pdf_to_xml(self, fio, file_path, config):
        temp_dir = config.get('temp_dir')

        if config.get('TIKA_URI'):
            return self.pdf_to_xml_tika(fio, config['TIKA_URI'], temp_dir)
        elif config.get('PDFTOHTML_BIN'):
            return self.pdf_to_xml_poppler(
                file_path, config['PDFTOHTML_BIN'], temp_dir)
        elif find_executable('pdftohtml'):
            return self.pdf_to_xml_poppler(
                file_path, find_executable('pdftohtml'), temp_dir)
        else:
            return RuntimeError('No PDF extraction tools available.')

    def pdf_to_xml_poppler(self, file_path, bin_path, temp_dir):
        self.logger.info(
            'Converting %r using %r...', file_path, bin_path)

        out_file = os.path.join(temp_dir, 'pdf.xml')
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
        assert retcode == 0, 'Execution failed: %r'.format(pdftohtml)
        assert os.path.exists(out_file), 'File missing: %r'.format(out_file)

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
