import logging
from PyPDF2 import PdfFileReader
from PyPDF2.utils import PdfReadError

from ingestors.base import Ingestor
from ingestors.support.pdf import PDFSupport

log = logging.getLogger(__name__)


class PDFIngestor(Ingestor, PDFSupport):
    """PDF file ingestor class.

    Extracts the text from the document by converting it first to XML.
    Splits the file into pages.
    """
    MAGIC = '%PDF-1.'
    MIME_TYPES = ['application/pdf']
    EXTENSIONS = ['pdf']
    SCORE = 5

    def extract_xmp_metadata(self, pdf):
        try:
            xmp = pdf.getXmpMetadata()
            if xmp is None:
                return
            self.update('message_id', xmp.xmpmm_documentId)
            for lang, title in xmp.dc_title.items():
                self.update('title', title)
                self.result.emit_language(lang)
            self.update('generator', xmp.pdf_producer)
            self.result.emit_language(xmp.dc_language)
            try:
                self.update('created_at', xmp.xmp_createDate)
            except Exception:
                pass
            try:
                self.update('modified_at', xmp.xmp_modifyDate)
            except Exception:
                pass
        except Exception as ex:
            log.warning("Error reading XMP: %r", ex)

    def extract_metadata(self, file_path):
        with open(file_path, 'rb') as fh:
            pdf = PdfFileReader(fh, strict=False)
            meta = pdf.getDocumentInfo()
            if meta is not None:
                self.update('title', meta.title)
                self.update('author', meta.author)
                self.update('generator', meta.creator)
                self.update('generator', meta.producer)
                if meta.subject:
                    self.result.emit_keyword(meta.subject)

            self.extract_xmp_metadata(pdf)
        # from pprint import pprint
        # pprint(self.result.to_dict())

    def ingest(self, file_path):
        """Ingestor implementation."""
        try:
            self.extract_metadata(file_path)
        except PdfReadError as rex:
            log.warning("PDF error: %s", rex)
        except Exception:
            # don't bail entirely, perhaps poppler knows how to deal.
            log.warning('Cannot read PDF: %s', file_path)
        self.pdf_extract(file_path)

    @classmethod
    def match(cls, file_path, result=None):
        score = super(PDFIngestor, cls).match(file_path, result=result)
        if score <= 0:
            with open(file_path, 'r') as fh:
                if fh.read(len(cls.MAGIC)) == cls.MAGIC:
                    return cls.SCORE * 2
        return score
