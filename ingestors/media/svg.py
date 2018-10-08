import logging

from ingestors.base import Ingestor
from ingestors.support.pdf import PDFSupport
from ingestors.util import join_path

log = logging.getLogger(__name__)


class SVGIngestor(Ingestor, PDFSupport):
    MIME_TYPES = [
        'image/svg+xml'
    ]
    EXTENSIONS = ['svg']
    SCORE = 20

    def ingest(self, file_path):
        pdf_path = join_path(self.work_path, 'image.pdf')
        self.exec_command('rsvg-convert',
                          file_path,
                          '-d', '300',
                          '-p', '300',
                          '-f', 'pdf',
                          '-o', pdf_path)
        self.assert_outfile(pdf_path)
        self.result.flag(self.result.FLAG_IMAGE)
        self.pdf_alternative_extract(pdf_path)
