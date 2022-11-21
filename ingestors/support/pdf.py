from binascii import b2a_hex
from dataclasses import dataclass
from io import StringIO
import logging
import os
from typing import Dict, List
import uuid

from pdfreader import SimplePDFViewer
from pdfreader.viewer import SimpleCanvas

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
            viewer = SimplePDFViewer(pdf_file)
            for page_number, page in enumerate(viewer, 1):
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

    def pdf_extract_page(self, page: SimpleCanvas, page_number: int) -> PdfPageModel:
        """Extract the contents of a single PDF page, using OCR if need be."""
        page_model = PdfPageModel(number=page_number, text="")
        texts = page.strings
        # print(f"Also found {len(page.canvas.inline_images)} images")

        # temp_dir = "/tests"
        # self._parse_images(device.get_result(), page_number, temp_dir)
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
