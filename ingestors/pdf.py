import os

from .ingestor import Ingestor, Result
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
            config['temp_dir'] = temp_dir

            xml, page_selector = self.pdf_to_xml(
                self.fio, self.file_path, config)

            for page in self.xml_to_text(xml, page_selector):
                ok, pagenum, text = page

                # TODO:
                # if not ok:
                #     self.ocr_image()

                self.children.append(
                    Result(content=text, order=pagenum)
                )

        if len(self.children) == 1:
            self.children.pop()
            self.result.order = pagenum
            self.result.content = text

        config.pop('temp_dir')
