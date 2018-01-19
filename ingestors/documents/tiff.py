import logging

from ingestors.base import Ingestor
from ingestors.support.pdf import PDFSupport
from ingestors.util import join_path

log = logging.getLogger(__name__)


class TIFFIngestor(Ingestor, PDFSupport):
    """TIFF appears to not really be an image format. Who knew?"""

    MIME_TYPES = [
        'image/tiff',
        'image/x-tiff',
    ]
    EXTENSIONS = ['tif', 'tiff']
    SCORE = 6

    def ingest(self, file_path):
        self.result.flag(self.result.FLAG_PDF)
        with self.create_temp_dir() as temp_dir:
            pdf_path = join_path(temp_dir, 'tiff.pdf')
            self.exec_command('convert',
                              file_path,
                              '-density', '300',
                              pdf_path)
            self.assert_outfile(pdf_path)
            self.pdf_alternative_extract(pdf_path)
