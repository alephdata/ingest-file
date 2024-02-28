from followthemoney import model

from ingestors.ingestor import Ingestor
from ingestors.support.pdf import PDFSupport
from ingestors.support.shell import ShellSupport
from ingestors.support.temp import TempFileSupport
from ingestors.exc import ProcessingException


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
        try:
            self.exec_command(
                "tiff2pdf",
                file_path,
                "-n",
                "-j",
                "-x",
                "300",
                "-y",
                "300",
                "-o",
                pdf_path,
            )
        except ProcessingException:
            self.exec_command(
                "tiff2pdf", file_path, "-x", "300", "-y", "300", "-o", pdf_path
            )

        self.assert_outfile(pdf_path)

        self.pdf_alternative_extract(entity, pdf_path, self.manager)
