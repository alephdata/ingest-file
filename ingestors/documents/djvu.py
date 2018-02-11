from ingestors.base import Ingestor
from ingestors.support.pdf import PDFSupport
from ingestors.util import join_path


class DjVuIngestor(Ingestor, PDFSupport):
    """Read DejaVu E-Books."""
    MIME_TYPES = [
        'image/vnd.djvu',
        'image/x.djvu',
        'image/x-djvu',
        'image/djvu',
    ]  # noqa

    def ingest(self, file_path):
        """Ingestor implementation."""
        self.result.flag(self.result.FLAG_PDF)
        pdf_path = join_path(self.work_path, 'page.pdf')
        self.exec_command('ddjvu',
                          '-format=pdf',
                          '-quality=100',
                          '-skip',
                          file_path,
                          pdf_path)
        self.assert_outfile(pdf_path)
        self.pdf_alternative_extract(pdf_path)
