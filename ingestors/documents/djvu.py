from ingestors.base import Ingestor
from ingestors.support.pdf import PDFSupport
from ingestors.util import join_path


class DjVuIngestor(Ingestor, PDFSupport):
    """Read DejaVu E-Books."""
    MIME_TYPES = ['image/vnd.djvu', 'image/x.djvu']  # noqa

    def ingest(self, file_path):
        """Ingestor implementation."""
        self.result.flag(self.result.FLAG_PDF)
        with self.create_temp_dir() as temp_dir:
            pdf_path = join_path(temp_dir, 'page.pdf')
            self.exec_command('ddjvu',
                              '-format=pdf',
                              '-quality=100',
                              '-skip',
                              file_path,
                              pdf_path)
            self.assert_outfile(pdf_path)
            self.pdf_alternative_extract(pdf_path)
