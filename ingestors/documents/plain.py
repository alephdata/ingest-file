import os

from ingestors.base import Ingestor
from ingestors.support.encoding import EncodingSupport
from ingestors.support.soffice import LibreOfficeSupport
from ingestors.exc import ProcessingException
from ingestors.util import join_path


class PlainTextIngestor(Ingestor, EncodingSupport, LibreOfficeSupport):
    """Plan text file ingestor class.

    Extracts the text from the document and enforces unicode on it.
    """
    MIME_TYPES = ['text/plain']
    MAX_SIZE = 2 * 1024 * 1024
    SCORE = 1

    def ingest(self, file_path):
        """Ingestor implementation."""
        file_size = self.result.size or os.path.getsize(file_path)
        if file_size > self.MAX_SIZE:
            raise ProcessingException("Text file is too large.")

        text = self.read_file_decoded(file_path)
        if text is None:
            raise ProcessingException("Document could not be decoded.")
        if len(text.strip()) == 0:
            raise ProcessingException("Document is empty.")

        with self.create_temp_dir() as temp_dir:
            text_path = join_path(temp_dir, 'page.txt')
            with open(text_path, 'wb') as fh:
                fh.write(text.encode('utf-8'))

            pdf_path = self.document_to_pdf(text_path, temp_dir)
            self.pdf_alternative_extract(pdf_path)
