import os
import logging
from unicodecsv import DictWriter

from messytables import any_tableset, offset_processor
from messytables import headers_guess, headers_processor

from ingestors.base import Ingestor
from ingestors.support.temp import TempFileSupport
from ingestors.util import string_value

log = logging.getLogger(__name__)


class MessyTablesIngestor(Ingestor, TempFileSupport):
    MIME_TYPES = [
        'application/excel',
        'application/x-excel',
        'application/vnd.ms-excel',
        'application/x-msexcel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # noqa
        'application/vnd.oasis.opendocument.spreadsheet'
    ]
    EXTENSIONS = ['xls', 'xlsx', 'ods']
    SCORE = 4

    def generate_csv(self, sheet, row_set, temp_dir):
        out_path = os.path.join(temp_dir, '%s.csv' % row_set.name)
        offset, headers = headers_guess(row_set.sample)
        row_set.register_processor(headers_processor(headers))
        row_set.register_processor(offset_processor(offset + 1))
        with open(out_path, 'w') as fh:
            writer = DictWriter(fh, headers)
            writer.writeheader()
            for row in row_set:
                data = {c.column: string_value(c.value) for c in row}
                writer.writerow(data)

        self.manager.handle_child(self.result, out_path,
                                  file_name=row_set.name,
                                  mime_type='text/csv')

    def ingest(self, file_path):
        with self.create_temp_dir() as temp_dir:
            with open(file_path, 'rb') as fh:
                table_set = any_tableset(fh,
                                         # extension=self.result.extension,
                                         mimetype=self.result.mime_type,
                                         window=20000)
                for sheet, row_set in enumerate(table_set.tables):
                    self.generate_csv(sheet, row_set, temp_dir)
