from __future__ import absolute_import
from dbf import Table
from collections import OrderedDict

from ingestors.base import Ingestor
from ingestors.util import safe_string


class DBFIngestor(Ingestor):
    MIME_TYPES = [
        'application/dbase',
        'application/x-dbase',
        'application/dbf',
        'application/x-dbf'
    ]
    EXTENSIONS = ['dbf']
    BASE_SCORE = 7

    def generate_rows(self, table):
        headers = [safe_string(h) for h in table.field_names]
        for row in table:
            data = OrderedDict()
            for header, value in zip(headers, row):
                data[header] = safe_string(value)
            yield data

    def ingest(self, file_path):
        table = Table(file_path).open()
        self.result.flag(self.result.FLAG_TABULAR)
        self.result.emit_rows(self.generate_rows(table))
