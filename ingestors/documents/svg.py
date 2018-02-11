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
        self.exec_command('convert',
                          file_path,
                          '-density', '300',
                          '-define',
                          'pdf:fit-page=A4',
                          pdf_path)
        self.assert_outfile(pdf_path)
        self.result.flag(self.result.FLAG_IMAGE)
        self.pdf_alternative_extract(pdf_path)
