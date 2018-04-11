import logging
from openpyxl import load_workbook

from ingestors.base import Ingestor
from ingestors.support.csv import CSVEmitterSupport
from ingestors.support.ooxml import OOXMLSupport
from ingestors.exc import ProcessingException
from ingestors.util import safe_string

log = logging.getLogger(__name__)


class ExcelXMLIngestor(Ingestor, CSVEmitterSupport, OOXMLSupport):
    MIME_TYPES = [
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # noqa
        'application/vnd.openxmlformats-officedocument.spreadsheetml.template',  # noqa
    ]
    EXTENSIONS = [
        'xlsx',
        'xlsm',
        'xltx',
        'xltm'
    ]
    SCORE = 6

    def generate_csv(self, sheet):
        for row in sheet.rows:
            try:
                yield [safe_string(c.value) for c in row]
            except (ValueError, OverflowError) as ve:
                log.warning("Failed to read Excel row: %s", ve)

    def ingest(self, file_path):
        self.ooxml_extract_metadata(file_path)
        try:
            book = load_workbook(file_path, read_only=True)
        except Exception as err:
            raise ProcessingException('Invalid Excel file: %s' % err)

        self.result.flag(self.result.FLAG_WORKBOOK)
        try:
            for name in book.sheetnames:
                rows = self.generate_csv(book[name])
                self.csv_child_iter(rows, name)
        finally:
            book.close()
