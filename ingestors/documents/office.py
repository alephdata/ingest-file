from ingestors.base import Ingestor
from ingestors.support.soffice import LibreOfficeSupport
from ingestors.support.ole import OLESupport


class DocumentIngestor(Ingestor, LibreOfficeSupport, OLESupport):
    """Office/Word document ingestor class.

    Converts the document to PDF and extracts the text.
    Mostly a slightly adjusted PDF ingestor.

    Requires system tools:

    - Open/Libre Office with dependencies
    - image ingestor dependencies to cover any embeded images OCR

    """

    MIME_TYPES = [
        # Text documents
        'text/richtext',
        'text/rtf',
        'application/rtf',
        'application/x-rtf',
        'application/msword',
        'application/vnd.ms-word',
        'application/wordperfect',
        'application/vnd.wordperfect',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # noqa

        # Presentations
        'application/vnd.ms-powerpoint',
        'application/vnd.sun.xml.impress',
        'application/vnd.ms-powerpoint.presentation',
        'application/vnd.ms-powerpoint.presentation.12',
        'application/vnd.openxmlformats-officedocument.presentationml.slideshow',  # noqa
        'application/vnd.openxmlformats-officedocument.presentationml.presentation',  # noqa

        # MS Office files with short stream missing
        'application/CDFV2-unknown',
        'application/CDFV2-corrupt'
    ]
    EXTENSIONS = ['docx', 'doc', 'ppt', 'pptx']
    SCORE = 5

    def ingest(self, file_path):
        """Ingestor implementation."""
        self.ole_extract_metadata(file_path)
        with self.create_temp_dir() as temp_dir:
            pdf_path = self.document_to_pdf(file_path, temp_dir)
            self.pdf_alternative_extract(pdf_path)
