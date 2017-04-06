import io
import os

from .pdf import PDFIngestor
from .support.office import OfficeSupport


class DocumentIngestor(PDFIngestor, OfficeSupport):
    """Office/Word document ingestor class.

    Converts the document to PDF and extracts the text.

    Requires system tools:

    - unoconv (will bring Open/Libre Office dependencies)
    - image ingestor dependencies to cover any embeded images OCR

    """

    MIME_TYPES = [
        # Text documents
        'text/richtext',
        'application/rtf',
        'application/x-rtf',
        'application/msword',
        'application/wordperfect',
        'application/vnd.wordperfect'
        'application/vnd.oasis.opendocument.text',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # noqa
        # Presentations
        'application/vnd.ms-powerpoint',
        'application/vnd.sun.xml.impress'
        'application/vnd.ms-powerpoint.presentation',
        'application/vnd.oasis.opendocument.presentation',
        'application/vnd.openxmlformats-officedocument.presentationml.slideshow',  # noqa
        'application/vnd.openxmlformats-officedocument.presentationml.presentation',  # noqa
    ]

    def configure(self):
        """Ingestor configuration."""
        config = super(DocumentIngestor, self).configure()
        config['UNOCONV_BIN'] = os.environ.get('UNOCONV_BIN')
        return config

    def ingest(self, config):
        """Ingestor implementation."""
        with self.create_temp_dir() as temp_dir:

            pdf_path = self.doc_to_pdf(
                self.fio, self.file_path, temp_dir, config)

            with io.open(pdf_path, 'rb') as pdfio:
                xml, page_selector = self.pdf_to_xml(
                    pdfio, pdf_path, temp_dir, config)

                # Pass pages similar to the way PDF is handling it.
                for page in self.xml_to_text(xml, page_selector):
                    self.add_child(page, pdf_path, temp_dir, config)

                for child in self.children:
                    child.run()
                    child.fio.close()
