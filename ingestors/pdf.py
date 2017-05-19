import os
import io

from .ingestor import Ingestor
from .image import ImageIngestor
from .html import HTMLIngestor
from .support.pdf import PDFSupport
from .support.fs import FSSupport
from .support.xml import XMLSupport


class PDFIngestor(Ingestor, PDFSupport, FSSupport, XMLSupport):
    """PDF file ingestor class.

    Extracts the text from the document by converting it first to XML.
    Splits the file into pages.
    """

    MIME_TYPES = ['application/pdf']

    def configure(self):
        """Ingestor configuration."""
        config = super(PDFIngestor, self).configure()

        config['TIKA_URI'] = os.environ.get('TIKA_URI')
        config['PDFTOHTML_BIN'] = os.environ.get('PDFTOHTML_BIN')
        config['PDFTOPPM_BIN'] = os.environ.get('PDFTOPPM_BIN')

        return config

    def ingest(self, config):
        """Ingestor implementation."""
        with self.create_temp_dir() as temp_dir:
            xml, page_selector = self.pdf_to_xml(
                self.fio, self.file_path, temp_dir, config)

            for page in self.xml_to_pages(xml, page_selector):
                self.add_page(page, self.file_path, temp_dir, config)

    def add_page(self, page, file_path, temp_dir, config):
        """Detaches every page to specific ingestors."""
        needs_ocr, text = self.page_to_text(page)
        pagenum = int(page.get('number') or 0)

        if not needs_ocr:
            ingestor_class = HTMLIngestor
            fio = io.BytesIO(bytearray(text, 'utf-8'))
            mime_type = HTMLIngestor.MIME_TYPES[0]
            file_path = ''
        else:
            file_path = self.pdf_page_to_image(
                pagenum,
                file_path,
                config['PDFTOPPM_BIN'],
                temp_dir
            )

            ingestor_class = ImageIngestor
            fio = io.open(file_path, 'rb')
            mime_type = ImageIngestor.MIME_TYPES[0]

        with fio:
            self.detach(
                ingestor_class=ingestor_class,
                fio=fio,
                file_path=file_path,
                mime_type=mime_type,
                extra={'order': pagenum}
            )
