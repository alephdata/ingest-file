import os
import glob
import uuid
from pdflib import Document
from normality import stringify

from ingestors.services import get_ocr, get_convert
from ingestors.support.temp import TempFileSupport
from ingestors.support.shell import ShellSupport


class PDFSupport(ShellSupport, TempFileSupport):
    """Provides helpers for PDF file context extraction."""

    def pdf_extract(self, pdf):
        """Extract pages and page text from a PDF file."""
        self.result.flag(self.result.FLAG_PDF)
        temp_dir = self.make_empty_directory()
        for page in pdf:
            self.pdf_extract_page(temp_dir, page)

    def pdf_alternative_extract(self, pdf_path):
        pdf = Document(pdf_path.encode('utf-8'))
        self.pdf_extract(pdf)

    def document_to_pdf(self, file_path):
        """Convert an office document into a PDF file."""
        converter = get_convert()
        return converter.document_to_pdf(file_path,
                                         self.result,
                                         self.work_path,
                                         self.manager.archive)

    def pdf_extract_page(self, temp_dir, page):
        """Extract the contents of a single PDF page, using OCR if need be."""
        pagenum = page.page_no
        texts = page.lines

        image_path = os.path.join(temp_dir, str(uuid.uuid4()))
        page.extract_images(path=image_path.encode('utf-8'), prefix=b'img')
        ocr = get_ocr()
        languages = self.result.ocr_languages
        for image_file in glob.glob(os.path.join(image_path, "*.png")):
            with open(image_file, 'rb') as fh:
                data = fh.read()
                text = ocr.extract_text(data, languages=languages)
                text = stringify(text)
                if text is not None:
                    texts.append(text)

        text = ' \n'.join(texts).strip()
        self.result.emit_page(int(pagenum), text)
