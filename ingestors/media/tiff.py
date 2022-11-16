from ingestors.log import get_logger
from followthemoney import model

from ingestors.ingestor import Ingestor
from ingestors.support.pdf import PDFSupport
from ingestors.support.shell import ShellSupport
from ingestors.support.temp import TempFileSupport

log = get_logger(__name__)


class TIFFIngestor(Ingestor, PDFSupport, TempFileSupport, ShellSupport):
    """TIFF appears to not really be an image format. Who knew?"""

    MIME_TYPES = [
        "image/tiff",
        "image/x-tiff",
    ]
    EXTENSIONS = ["tif", "tiff"]
    SCORE = 11

    def ingest(self, file_path, entity):
        entity.schema = model.get("Pages")
        pdf_path = self.make_work_file("tiff.pdf")
        self.exec_command(
            "tiff2pdf", file_path, "-x", "300", "-y", "300", "-o", pdf_path
        )
        self.assert_outfile(pdf_path)
        self.pdf_alternative_extract(entity, pdf_path)
