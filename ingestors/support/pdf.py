from dataclasses import dataclass
from io import StringIO
import logging
from typing import Dict, List
import uuid

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfparser import PDFParser

from normality import collapse_spaces  # noqa

from ingestors.support.ocr import OCRSupport
from ingestors.support.convert import DocumentConvertSupport

logging.getLogger("pdfminer").setLevel(logging.WARNING)


@dataclass
class PdfPageModel:
    number: int
    text: str


@dataclass
class PdfModel:
    metadata: Dict[str, str]
    xmp_metadata: Dict[str, str]
    pages: List[PdfPageModel]


class PDFSupport(DocumentConvertSupport, OCRSupport):
    """Provides helpers for PDF file context extraction."""

    def parse(self, file_path: str) -> PdfModel:
        model = PdfModel(metadata=None, xmp_metadata=None, pages=[])
        with open(file_path, "rb") as pdf_file:
            parser = PDFParser(pdf_file)
            pdf_doc = PDFDocument(parser)
            for page_number, page in enumerate(PDFPage.create_pages(pdf_doc), 1):
                model.pages.append(self.pdf_extract_page(page, page_number))
        return model

    def pdf_alternative_extract(self, entity, pdf_path):
        checksum = self.manager.store(pdf_path)
        entity.set("pdfHash", checksum)
        pdf = PDFDocument(bytes(pdf_path))
        self.pdf_extract(entity, pdf)

    def pdf_extract_page(self, page: PDFPage, page_number: int) -> PdfPageModel:
        """Extract the contents of a single PDF page, using OCR if need be."""
        page_model = PdfPageModel(number=page_number, text="")
        buf = StringIO()
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, buf, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        interpreter.process_page(page)
        texts = buf.getvalue()
        # temp_dir = self.make_empty_directory()
        # image_path = temp_dir.joinpath(str(uuid.uuid4()))
        # page.extract_images(path=bytes(image_path), prefix=b"img")
        # languages = self.manager.context.get("languages")
        # for image_file in image_path.glob("*.png"):
        #    with open(image_file, "rb") as fh:
        #        data = fh.read()
        #        text = self.extract_ocr_text(data, languages=languages)
        #        if text is not None:
        #            texts.append(text)

        text = " \n".join(texts).strip()
        page_model.text = texts
        return page_model
