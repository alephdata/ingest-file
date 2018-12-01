import logging

from ingestors.ingestor import Ingestor
from ingestors.support.pdf import PDFSupport
from ingestors.util import join_path

log = logging.getLogger(__name__)


class TIFFIngestor(Ingestor, PDFSupport):
    """TIFF appears to not really be an image format. Who knew?"""

    MIME_TYPES = [
        'image/tiff',
        'image/x-tiff',
    ]
    EXTENSIONS = [
        'tif',
        'tiff'
    ]
    SCORE = 11

    def ingest(self, file_path):
        self.result.flag(self.result.FLAG_PDF)
        pdf_path = join_path(self.work_path, 'tiff.pdf')
        self.exec_command('tiff2pdf',
                          file_path,
                          '-x', '300',
                          '-y', '300',
                          '-o', pdf_path)
        self.assert_outfile(pdf_path)
        self.pdf_alternative_extract(pdf_path)
