import logging

from ingestors.ingestor import Ingestor
from ingestors.support.pdf import PDFSupport, PdfModel
from ingestors.exc import ProcessingException


class PDFIngestor(Ingestor, PDFSupport):
    """PDF file ingestor class.

    Extracts the text from the document by converting it first to XML.
    Splits the file into pages.
    """

    MAGIC = "%PDF-1."
    MIME_TYPES = ["application/pdf"]
    EXTENSIONS = ["pdf"]
    SCORE = 6

    def ingest(self, file_path, entity):
        """Ingestor implementation."""
        try:
            self.parse_and_ingest(file_path, entity, self.manager)
        except Exception as ex:
            raise ProcessingException("Could not extract PDF file: %r" % ex) from ex

    @classmethod
    def match(cls, file_path, entity):
        score = super(PDFIngestor, cls).match(file_path, entity)
        if score <= 0:
            with open(file_path, "rb") as fh:
                if fh.read(len(cls.MAGIC)) == cls.MAGIC:
                    return cls.SCORE * 2
        return score
