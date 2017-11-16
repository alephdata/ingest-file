import xlrd
import logging
from time import time
from datetime import datetime
from xlrd.biffh import XLRDError
from normality import stringify

from ingestors.base import Ingestor
from ingestors.support.csv import CSVEmitterSupport
from ingestors.support.ole import OLESupport
from ingestors.exc import ProcessingException

log = logging.getLogger(__name__)


class ExcelIngestor(Ingestor, CSVEmitterSupport, OLESupport):
    MIME_TYPES = [
        'application/excel',
        'application/x-excel',
        'application/vnd.ms-excel',
        'application/x-msexcel',
    ]
    EXTENSIONS = ['xls', 'xlt', 'xla']
    SCORE = 6

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
        return stringify(value)

    def generate_csv(self, sheet):
        for row_index in xrange(0, sheet.nrows):
            yield [self.convert_cell(c, sheet) for c in sheet.row(row_index)]

    def ingest(self, file_path):
        self.ole_extract_metadata(file_path)
        try:
            book = xlrd.open_workbook(file_path, formatting_info=False)
            # if self.result.author is None:
            #     self.result.author = book.user_name
        except Exception as err:
            raise ProcessingException('Invalid Excel file: %s' % err)

        try:
            for sheet in book.sheets():
                rows = self.generate_csv(sheet)
                self.csv_child_iter(rows, sheet.name)
        except XLRDError as err:
            raise ProcessingException('Invalid Excel file: %s' % err)
        finally:
            book.release_resources()
