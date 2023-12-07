import logging

from ingestors.ingestor import Ingestor
from ingestors.support.pdf import PDFSupport
from ingestors.exc import ProcessingException, UnauthorizedError, ENCRYPTED_MSG

log = logging.getLogger(__name__)


class PDFIngestor(Ingestor, PDFSupport):
    """PDF file ingestor class.

    Extracts the text from the document by converting it first to XML.
    Splits the file into pages.
    """

    MAGIC = "%PDF-1."
    MIME_TYPES = ["application/pdf"]
    EXTENSIONS = ["pdf"]
    SCORE = 6

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
            if "creationdate" in meta:
                entity.add("authoredAt", meta.get("creationdate"))
            if "moddate" in meta:
                entity.add("modifiedAt", meta.get("moddate"))

    def ingest(self, file_path, entity):
        """Ingestor implementation."""
        try:
            self.parse_and_ingest(file_path, entity, self.manager)
        except UnauthorizedError as pwe:
            raise ProcessingException(ENCRYPTED_MSG) from pwe
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
