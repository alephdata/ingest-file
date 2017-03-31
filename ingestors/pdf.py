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

            for page in self.xml_to_text(xml, page_selector):
                needs_ocr, text = self.page_to_text(page)
                pagenum = page.get('number') or 0

                if not needs_ocr:
                    child = HTMLIngestor(
                        fio=io.StringIO(text),
                        file_path=self.file_path,
                        parent=self
                    )
                else:
                    page_image_path = self.pdf_page_to_image(
                        pagenum,
                        self.file_path,
                        config['PDFTOPPM_BIN'],
                        temp_dir
                    )

                    child = ImageIngestor(
                        fio=io.open(page_image_path, 'rb'),
                        file_path=page_image_path,
                        parent=self
                    )

                child.result.order = pagenum
                self.children.append(child)

            for child in self.children:
                child.run()
                child.fio.close()
