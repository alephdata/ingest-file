import os
import glob
import uuid

from normality import collapse_spaces  # noqa
from pdflib import Document

from ingestors.support.temp import TempFileSupport
from ingestors.support.shell import ShellSupport
from ingestors.support.ocr import OCRSupport


class PDFSupport(ShellSupport, TempFileSupport, OCRSupport):
    """Provides helpers for PDF file context extraction."""

    def pdf_extract(self, pdf):
        """Extract pages and page text from a PDF file."""
        self.result.flag(self.result.FLAG_PDF)
        temp_dir = self.make_empty_directory()
        for page in pdf:
            self.pdf_extract_page(temp_dir, page)

    def pdf_alternative_extract(self, pdf_path):
        self.result.emit_pdf_alternative(pdf_path)
        pdf = Document(pdf_path.encode('utf-8'))
        self.pdf_extract(pdf)

    def pdf_extract_page(self, temp_dir, page):
        """Extract the contents of a single PDF page, using OCR if need be."""
        pagenum = page.page_no
        texts = page.lines

        image_path = os.path.join(temp_dir, str(uuid.uuid4()))
        page.extract_images(path=image_path.encode('utf-8'), prefix=b'img')
        for image_file in glob.glob(os.path.join(image_path, "*.png")):
            with open(image_file, 'rb') as fh:
                text = self.extract_text_from_image(fh.read())
                # text = collapse_spaces(text)
                if text is not None:
                    texts.append(text)

        text = ' \n'.join(texts).strip()
        self.result.emit_page(int(pagenum), text)
