import logging
from odf.teletype import extractText
from odf.table import TableRow, TableCell, Table
from odf.text import P
from odf.namespaces import OFFICENS
from followthemoney import model

from ingestors.ingestor import Ingestor
from ingestors.support.table import TableSupport
from ingestors.support.opendoc import OpenDocumentSupport

log = logging.getLogger(__name__)


class OpenOfficeSpreadsheetIngestor(Ingestor, TableSupport, OpenDocumentSupport):
    MIME_TYPES = [
        "application/vnd.oasis.opendocument.spreadsheet",
        "application/vnd.oasis.opendocument.spreadsheet-template",
    ]
    EXTENSIONS = ["ods", "ots"]
    SCORE = 7
    VALUE_FIELDS = ["date-value", "time-value", "boolean-value", "value"]

    def convert_cell(self, cell):
        cell_type = cell.getAttrNS(OFFICENS, "value-type")
        if cell_type == "currency":
            value = cell.getAttrNS(OFFICENS, "value")
            currency = cell.getAttrNS(OFFICENS, cell_type)
            if value is None:
                return None
            if currency is None:
                return value
            return value + " " + currency

        for field in self.VALUE_FIELDS:
            value = cell.getAttrNS(OFFICENS, field)
            if value is not None:
                return value

        return self.read_text_cell(cell)

    def read_text_cell(self, cell):
        content = []
        for paragraph in cell.getElementsByType(P):
            content.append(extractText(paragraph))
        return "\n".join(content)

    def generate_csv(self, table):
        for row in table.getElementsByType(TableRow):
            values = []
            for cell in row.getElementsByType(TableCell):
                repeat = cell.getAttribute("numbercolumnsrepeated") or 1
                value = self.convert_cell(cell)
                for i in range(int(repeat)):
                    values.append(value)
            yield values

    def ingest(self, file_path, entity):
        entity.schema = model.get("Workbook")
        doc = self.parse_opendocument(file_path, entity)
        for sheet in doc.spreadsheet.getElementsByType(Table):
            name = sheet.getAttribute("name")
            table = self.manager.make_entity("Table", parent=entity)
            table.make_id(entity.id, name)
            table.set("title", name)
            # add workbook metadata to individual tables
            for metadatum in [
                "authoredAt",
                "author",
                "summary",
                "generator",
                "date",
                "processingAgent",
            ]:
                table.set(metadatum, entity.get(metadatum))
            # Emit a partial table fragment with parent reference and name
            # early, so that we don't have orphan fragments in case of an error
            # in the middle of processing.
            # See https://github.com/alephdata/ingest-file/issues/171
            self.manager.emit_entity(table, fragment="initial")
            self.emit_row_tuples(table, self.generate_csv(sheet))
            if table.has("csvHash"):
                self.manager.emit_entity(table)
