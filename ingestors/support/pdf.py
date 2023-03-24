from dataclasses import dataclass
import logging
import os
from typing import Dict, List
import uuid
import unicodedata

import fitz

from normality import collapse_spaces  # noqa

from followthemoney import model
from ingestors.exc import UnauthorizedError
from ingestors.support.ocr import OCRSupport
from ingestors.support.convert import DocumentConvertSupport

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

    def extract_xmp_metadata(self, pdf: PdfModel, entity):
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

    def extract_metadata(self, pdf: PdfModel, entity):
        meta = pdf.metadata
        if meta is not None:
            entity.add("title", meta.get("title"))
            entity.add("author", meta.get("author"))
            entity.add("generator", meta.get("creator"))
            entity.add("generator", meta.get("producer"))
            entity.add("keywords", meta.get("subject"))

    def extract_pages(self, pdf_model: PdfModel, entity, manager):
        entity.schema = model.get("Pages")
        for page_model in pdf_model.pages:
            page_entity = self.manager.make_entity("Page")
            page_entity.make_id(entity.id, page_model.number)
            page_entity.set("document", entity)
            page_entity.set("index", page_model.number)
            page_entity.add("bodyText", page_model.text)
            manager.apply_context(page_entity, entity)
            manager.emit_entity(page_entity)
            manager.emit_text_fragment(entity, page_model.text, page_entity.id)

    def parse(self, file_path: str) -> PdfModel:
        """Takes a file_path to a pdf and returns a `PdfModel`"""
        pdf_model = PdfModel(metadata=None, xmp_metadata=None, pages=[])
        with fitz.open(file_path) as pdf_doc:
            if pdf_doc.needs_pass:
                raise UnauthorizedError
            # print(f"\n[IF] number of pages: {pdf_doc.page_count}")
            for page_num in range(pdf_doc.page_count):
                pdf_model.pages.append(
                    self.pdf_extract_page(pdf_doc, pdf_doc[page_num], page_num)
                )
        return pdf_model

    def parse_and_ingest(self, file_path: str, entity, manager):
        pdf_model: PdfModel = self.parse(file_path)
        self.extract_metadata(pdf_model, entity)
        self.extract_xmp_metadata(pdf_model, entity)
        self.extract_pages(pdf_model, entity, manager)

    def pdf_alternative_extract(self, entity, pdf_path: str, manager):
        checksum = self.manager.store(pdf_path)
        entity.set("pdfHash", checksum)
        self.parse_and_ingest(pdf_path, entity, manager)

    def pdf_extract_page(self, pdf_doc, page, page_number: int) -> PdfPageModel:
        """Extract the contents of a single PDF page, using OCR if need be."""
        # Extract text
        full_text = page.get_text()
        # print(f"[IF] extracted text: \n{full_text}")

        # Extract images
        images = page.get_images()

        # Create a temporary location to store all extracted images
        temp_dir = self.make_empty_directory()
        image_dir = temp_dir.joinpath(str(uuid.uuid4()))
        os.mkdir(image_dir)

        # Extract images from PDF and store them on the disk
        extracted_images = []
        for image_index, image in enumerate(images, start=1):
            xref = image[0]
            img = pdf_doc.extract_image(xref)
            if img:
                image_path = os.path.join(
                    image_dir, f"image{page_number+1}_{image_index}.{img['ext']}"
                )
                with open(image_path, "wb") as image_file:
                    image_file.write(img["image"])
                extracted_images.append(image_path)

        # Attempt to OCR the images and extract text
        languages = self.manager.context.get("languages")
        for image_path in extracted_images:
            with open(image_path, "rb") as fh:
                data = fh.read()
                text = self.extract_ocr_text(data, languages=languages)
                if text is not None:
                    # print(f"[IF] extracted text from images: \n{text}")
                    full_text += text

        full_text = unicodedata.normalize("NFKD", full_text.strip())
        return PdfPageModel(number=page_number + 1, text=full_text.strip())
