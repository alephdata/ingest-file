from __future__ import absolute_import
import six
from dbf import Table
from collections import OrderedDict

from ingestors.base import Ingestor


class DBFIngestor(Ingestor):
    MIME_TYPES = ['application/x-dbf']
    EXTENSIONS = ['dbf']
    BASE_SCORE = 7

    def generate_rows(self, table):
        for row in table:
            data = OrderedDict()
            for field, value in zip(table.field_names, row):
                if value is not None:
                    value = six.text_type(value).strip()
                    if not len(value):
                        value = None
                data[field] = value
            yield data

    def ingest(self, file_path):
        table = Table(file_path).open()
        self.result.emit_rows(self.generate_rows(table))
