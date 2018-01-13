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
    MIME_TYPES = ['application/pdf']

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
                    self.result.keywords.append(meta.subject)

            xmp = pdf.getXmpMetadata()
            if xmp is not None:
                self.update('id', xmp.xmpmm_documentId)
                for lang, title in xmp.dc_title.items():
                    self.update('title', title)
                    self.result.languages.append(lang)
                self.update('generator', xmp.pdf_producer)
                self.result.languages.extend(xmp.dc_language)
                try:
                    self.update('created_at', xmp.xmp_createDate)
                except Exception:
                    pass
                try:
                    self.update('modified_at', xmp.xmp_modifyDate)
                except Exception:
                    pass

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
            log.exception('Cannot read PDF: %s', file_path)
        self.pdf_extract(file_path)
