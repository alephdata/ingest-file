from ingestors.base import Ingestor
from ingestors.support.soffice import LibreOfficeSupport
from ingestors.support.ooxml import OOXMLSupport


class OfficeOpenXMLIngestor(Ingestor, LibreOfficeSupport, OOXMLSupport):
    """Office/Word document ingestor class.

    Converts the document to PDF and extracts the text.
    Mostly a slightly adjusted PDF ingestor.
    """

    PREFIX = 'application/vnd.openxmlformats-officedocument.'
    MIME_TYPES = [
        PREFIX + 'wordprocessingml.document',
        PREFIX + 'wordprocessingml.template',
        PREFIX + 'presentationml.slideshow',
        PREFIX + 'presentationml.presentation',
        PREFIX + 'presentationml.template',
        PREFIX + 'presentationml.slideshow',
    ]
    EXTENSIONS = ['docx', 'docm', 'dotx', 'potx', 'pptx', 'ppsx']
    SCORE = 5

    def ingest(self, file_path):
        """Ingestor implementation."""
        self.result.flag(self.result.FLAG_PDF)
        self.ooxml_extract_metadata(file_path)
        pdf_path = self.document_to_pdf(file_path)
        self.pdf_alternative_extract(pdf_path)
