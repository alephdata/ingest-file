import os

from ingestors.base import Ingestor
from ingestors.support.encoding import EncodingSupport
from ingestors.support.soffice import LibreOfficeSupport


class PlainTextIngestor(Ingestor, EncodingSupport, LibreOfficeSupport):
    """Plan text file ingestor class.

    Extracts the text from the document and enforces unicode on it.
    """
    MIME_TYPES = ['text/plain']

    def ingest(self, file_path):
        """Ingestor implementation."""
        text = self.read_file_decoded(file_path)
        with self.create_temp_dir() as temp_dir:
            text_path = os.path.join(temp_dir, 'page.txt')
            with open(text_path, 'wb') as fh:
                fh.write(text.encode('utf-8'))

            pdf_path = self.document_to_pdf(text_path, temp_dir)
            self.pdf_alternative_extract(pdf_path)
