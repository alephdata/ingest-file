import logging
from pdflib import Document

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
            xmp = pdf.xmp_metadata
            if xmp is None:
                return
            self.update('message_id', xmp['xmpmm'].get('documentid'))
            self.update('title', xmp['dc'].get('title'))
            self.update('generator', xmp['pdf'].get('producer'))
            self.result.emit_language(xmp['dc'].get('language'))
            self.update('created_at', xmp['xmp'].get('createdate'))
            self.update('modified_at', xmp['xmp'].get('modifydate'))
        except Exception as ex:
            log.warning("Error reading XMP: %r", ex)

    def extract_metadata(self, pdf):
        meta = pdf.metadata
        if meta is not None:
            self.update('title', meta.get("title"))
            self.update('author', meta.get("author"))
            self.update('generator', meta.get("creator"))
            self.update('generator', meta.get("producer"))
            self.result.emit_keyword(meta.get("subject"))

        self.extract_xmp_metadata(pdf)
        # from pprint import pprint
        # pprint(self.result.to_dict())

    def ingest(self, file_path):
        """Ingestor implementation."""
        try:
            pdf = Document(file_path.encode('utf-8'))
            self.extract_metadata(pdf)
            self.pdf_extract(pdf)
        except Exception:
            log.warning('Cannot read PDF: %s', file_path)

    @classmethod
    def match(cls, file_path, result=None):
        score = super(PDFIngestor, cls).match(file_path, result=result)
        if score <= 0:
            with open(file_path, 'rb') as fh:
                if fh.read(len(cls.MAGIC)) == cls.MAGIC:
                    return cls.SCORE * 2
        return score
