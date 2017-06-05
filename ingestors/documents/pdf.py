from ingestors.base import Ingestor
from ingestors.support.pdf import PDFSupport


class PDFIngestor(Ingestor, PDFSupport):
    """PDF file ingestor class.

    Extracts the text from the document by converting it first to XML.
    Splits the file into pages.
    """
    MIME_TYPES = ['application/pdf']

    def ingest(self, file_path):
        """Ingestor implementation."""
        self.pdf_extract(file_path)
