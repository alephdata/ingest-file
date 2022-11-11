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

from followthemoney import model
from ingestors.support.ocr import OCRSupport
from ingestors.support.convert import DocumentConvertSupport

# silence some shouty debug output from pdfminer
logging.getLogger("pdfminer").setLevel(logging.WARNING)

log = logging.getLogger(__name__)


@dataclass
class PdfPageModel:
    """Represents data extracted from a page in a PDF"""

    number: int
    text: str


@dataclass
class PdfModel:
    """Represents data extracted from a PDF"""

    metadata: Dict[str, str]
    xmp_metadata: Dict[str, str]
    pages: List[PdfPageModel]


class PDFSupport(DocumentConvertSupport, OCRSupport):
    """Provides helpers for PDF file context extraction."""

    def extract_xmp_metadata(self, pdf, entity):
        try:
            xmp = pdf.xmp_metadata
            if xmp is None:
                return
            entity.add("messageId", xmp["xmpmm"].get("documentid"))
            entity.add("title", xmp["dc"].get("title"))
            entity.add("generator", xmp["pdf"].get("producer"))
            entity.add("language", xmp["dc"].get("language"))
            entity.add("authoredAt", xmp["xmp"].get("createdate"))
            entity.add("modifiedAt", xmp["xmp"].get("modifydate"))
        except Exception as ex:
            log.warning("Error reading XMP: %r", ex)

    def extract_metadata(self, pdf, entity):
        meta = pdf.metadata
        if meta is not None:
            entity.add("title", meta.get("title"))
            entity.add("author", meta.get("author"))
            entity.add("generator", meta.get("creator"))
            entity.add("generator", meta.get("producer"))
            entity.add("keywords", meta.get("subject"))

    def extract_pages(self, pdf_model, entity, manager):
        entity.schema = model.get("Pages")
        for page_model in pdf_model.pages:
            page_entity = self.manager.make_entity("Page")
            page_entity.make_id(entity.id, page_model.number)
            page_entity.set("document", entity)
            page_entity.set("index", page_model.number)
            page_entity.add("bodyText", page_model.text)
            manager.apply_context(page_entity, entity)
            manager.emit_entity(page_entity)
            manager.emit_text_fragment(entity, page_model.text, entity.id)

    def parse(self, file_path: str) -> PdfModel:
        """Takes a file_path to a pdf and returns a `PdfModel`"""
        pdf_model = PdfModel(metadata=None, xmp_metadata=None, pages=[])
        with open(file_path, "rb") as pdf_file:
            parser = PDFParser(pdf_file)
            pdf_doc = PDFDocument(parser)
            for page_number, page in enumerate(PDFPage.create_pages(pdf_doc), 1):
                pdf_model.pages.append(self.pdf_extract_page(page, page_number))
        return pdf_model

    def parse_and_ingest(self, file_path, entity, manager):
        pdf_model: PdfModel = self.parse(file_path)
        self.extract_metadata(pdf_model, entity)
        self.extract_xmp_metadata(pdf_model, entity)
        self.extract_pages(pdf_model, entity, manager)

    def pdf_alternative_extract(self, entity, pdf_path, manager):
        checksum = self.manager.store(pdf_path)
        entity.set("pdfHash", checksum)
        self.parse_and_ingest(pdf_path, entity, manager)

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
