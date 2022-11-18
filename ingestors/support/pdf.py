from binascii import b2a_hex
from dataclasses import dataclass
from io import StringIO
import logging
import os
from typing import Dict, List
import uuid

from pdfminer.converter import TextConverter, PDFPageAggregator
from pdfminer.layout import LAParams, LTImage, LTFigure
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

    def _write_file(self, folder, filename, filedata, flags="w"):
        """Write the file data to the folder and filename combination
        (flags: 'w' for write text, 'wb' for write binary, use 'a' instead of 'w' for append)"""
        result = False
        if os.path.isdir(folder):
            try:
                file_obj = open(os.path.join(folder, filename), flags)
                file_obj.write(filedata)
                file_obj.close()
                result = True
            except IOError:
                pass
        return result

    def _determine_image_type(self, stream_first_4_bytes):
        """Find out the image file type based on the magic number comparison of the first 4 (or 2) bytes"""
        file_type = None
        bytes_as_hex = b2a_hex(stream_first_4_bytes)
        print(f"magic bytes {bytes_as_hex}")
        if bytes_as_hex.startswith(b"ffd8"):
            file_type = ".jpeg"
        elif bytes_as_hex == "89504e47":
            file_type = ".png"
        elif bytes_as_hex == "47494638":
            file_type = ".gif"
        elif bytes_as_hex.startswith(b"424d"):
            file_type = ".bmp"
        return file_type

    def _save_image(self, lt_image, page_number, images_folder):
        """Try to save the image data from this LTImage object, and return the file name, if successful"""
        result = None
        if lt_image.stream:
            file_stream = lt_image.stream.get_rawdata()
            if file_stream:
                first_bytes = file_stream[0:4]
                file_ext = self._determine_image_type(first_bytes) or "xxx"
                if file_ext:
                    file_name = "".join(
                        [str(page_number), "_", lt_image.name, file_ext]
                    )
                    if self._write_file(
                        images_folder, file_name, file_stream, flags="wb"
                    ):
                        result = file_name
                else:
                    log.debug(f"Unrecognized image starting with {first_bytes}")
        return result

    def _parse_images(self, layout, page_number, folder):
        for obj in layout:
            if isinstance(obj, LTImage):
                saved_file = self._save_image(obj, page_number, folder)
                print(f"Found {folder}/{saved_file}")
            elif isinstance(obj, LTFigure):
                self._parse_images(obj, page_number, folder)

    def pdf_extract_page(self, page: PDFPage, page_number: int) -> PdfPageModel:
        """Extract the contents of a single PDF page, using OCR if need be."""
        page_model = PdfPageModel(number=page_number, text="")
        buf = StringIO()
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, buf, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        interpreter.process_page(page)

        # images
        # temp_dir = self.make_empty_directory()
        temp_dir = "/tests"
        rsrcmgr = PDFResourceManager()
        device = PDFPageAggregator(rsrcmgr)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        interpreter.process_page(page)
        self._parse_images(device.get_result(), page_number, temp_dir)
        texts = buf.getvalue()
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
