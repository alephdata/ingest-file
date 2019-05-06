import xlrd
import logging
from time import time
from datetime import datetime
from xlrd.biffh import XLRDError
from followthemoney import model

from ingestors.ingestor import Ingestor
from ingestors.support.table import TableSupport
from ingestors.support.ole import OLESupport
from ingestors.exc import ProcessingException
from ingestors.util import safe_string

log = logging.getLogger(__name__)


class ExcelIngestor(Ingestor, TableSupport, OLESupport):
    MIME_TYPES = [
        'application/excel',
        'application/x-excel',
        'application/vnd.ms-excel',
        'application/x-msexcel',
    ]
    EXTENSIONS = [
        'xls',
        'xlt',
        'xla'
    ]
    SCORE = 7

    def convert_cell(self, cell, sheet):
        value = cell.value
        try:
            if cell.ctype == 3:
                if value == 0:
                    return None
                year, month, day, hour, minute, second = \
                    xlrd.xldate_as_tuple(value, sheet.book.datemode)
                if (year, month, day) == (0, 0, 0):
                    value = time(hour, minute, second)
                    return value.isoformat()
                else:
                    value = datetime(year, month, day, hour, minute, second)
                    return value.isoformat()
        except Exception:
            pass
        return safe_string(value)

    def generate_csv(self, sheet):
        for row_index in range(0, sheet.nrows):
            yield [self.convert_cell(c, sheet) for c in sheet.row(row_index)]

    def ingest(self, file_path, entity):
        entity.schema = model.get('Workbook')
        self.extract_ole_metadata(file_path, entity)
        try:
            book = xlrd.open_workbook(file_path, formatting_info=False)
        except Exception as err:
            raise ProcessingException('Invalid Excel file: %s' % err)

        try:
            for sheet in book.sheets():
                table = self.manager.make_entity('Table', parent=entity)
                table.make_id(entity, sheet.name)
                table.set('title', sheet.name)
                self.emit_row_tuples(table, self.generate_csv(sheet))
                self.manager.emit_entity(table)
        except XLRDError as err:
            raise ProcessingException('Invalid Excel file: %s' % err)
        finally:
            book.release_resources()
