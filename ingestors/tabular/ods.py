import logging
from odf.teletype import extractText
from odf.table import TableRow, TableCell, Table
from odf.text import P
from odf.namespaces import OFFICENS
from odf.opendocument import load
from normality import stringify

from ingestors.base import Ingestor
from ingestors.support.csv import CSVEmitterSupport

log = logging.getLogger(__name__)


class OpenOfficeSpreadsheetIngestor(Ingestor, CSVEmitterSupport):
    MIME_TYPES = [
        'application/vnd.oasis.opendocument.spreadsheet',
        'application/vnd.oasis.opendocument.spreadsheet-template'
    ]
    EXTENSIONS = ['ods', 'ots']
    SCORE = 6
    VALUE_FIELDS = [
        'date-value',
        'time-value',
        'boolean-value',
        'value'
    ]

    def convert_cell(self, cell):
        cell_type = cell.getAttrNS(OFFICENS, 'value-type')
        if cell_type == "currency":
            value = cell.getAttrNS(OFFICENS, 'value')
            currency = cell.getAttrNS(OFFICENS, cell_type)
            return value + ' ' + currency

        for field in self.VALUE_FIELDS:
            value = cell.getAttrNS(OFFICENS, field)
            if value is not None:
                return value

        return self.read_text_cell(cell)

    def read_text_cell(self, cell):
        content = []
        for paragraph in cell.getElementsByType(P):
            content.append(extractText(paragraph))
        return '\n'.join(content)

    def generate_csv(self, table):
        for row in table.getElementsByType(TableRow):
            values = []
            for cell in row.getElementsByType(TableCell):
                repeat = cell.getAttribute("numbercolumnsrepeated") or 1
                value = self.convert_cell(cell)
                value = stringify(value)
                for i in range(int(repeat)):
                    values.append(value)
            yield values

    def ingest(self, file_path):
        book = load(file_path)
        for table in book.spreadsheet.getElementsByType(Table):
            name = table.getAttribute('name')
            rows = self.generate_csv(table)
            self.csv_child_iter(rows, name)
