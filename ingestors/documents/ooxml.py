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
        self.ooxml_extract_metadata(file_path)
        with self.create_temp_dir() as temp_dir:
            pdf_path = self.document_to_pdf(file_path, temp_dir)
            self.pdf_alternative_extract(pdf_path)
