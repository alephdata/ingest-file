import logging
from openpyxl import load_workbook
from normality import stringify

from ingestors.base import Ingestor
from ingestors.support.csv import CSVEmitterSupport
from ingestors.exc import ProcessingException

log = logging.getLogger(__name__)


class ExcelXMLIngestor(Ingestor, CSVEmitterSupport):
    MIME_TYPES = [
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # noqa
        'application/vnd.openxmlformats-officedocument.spreadsheetml.template',  # noqa
    ]
    EXTENSIONS = ['xlsx', 'xlsm', 'xltx', 'xltm']
    SCORE = 6

    def generate_csv(self, sheet):
        for row in sheet.rows:
            yield [stringify(c.value) for c in row]

    def ingest(self, file_path):
        try:
            book = load_workbook(file_path, read_only=True)
        except Exception as err:
            raise ProcessingException('Invalid Excel file: %s' % err)

        try:
            for name in book.get_sheet_names():
                sheet = book.get_sheet_by_name(name)
                rows = self.generate_csv(sheet)
                self.csv_child_iter(rows, name)
        finally:
            book.close()
