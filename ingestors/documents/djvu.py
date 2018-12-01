from followthemoney import model

from ingestors.ingestor import Ingestor
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

    def ingest(self, file_path, entity):
        """Ingestor implementation."""
        entity.schema = model.get('Pages')
        pdf_path = join_path(self.work_path, 'page.pdf')
        self.exec_command('ddjvu',
                          '-format=pdf',
                          '-quality=100',
                          '-skip',
                          file_path,
                          pdf_path)
        self.assert_outfile(pdf_path)
        self.pdf_alternative_extract(entity, pdf_path)
