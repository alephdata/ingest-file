import os
import logging
from unicodecsv import DictWriter
from normality import safe_filename
from messytables import any_tableset, offset_processor
from messytables import headers_guess, headers_processor

from ingestors.base import Ingestor
from ingestors.support.temp import TempFileSupport
from ingestors.util import string_value, join_path

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
    NON_MIME_TYPES = [
        'application/zip'
    ]
    EXTENSIONS = ['xls', 'xlsx', 'ods']
    SCORE = 4

    def generate_csv(self, sheet, row_set, temp_dir):
        out_path = safe_filename(row_set.name, extension='csv')
        out_path = join_path(temp_dir, out_path)
        offset, headers = headers_guess(row_set.sample)
        row_set.register_processor(headers_processor(headers))
        row_set.register_processor(offset_processor(offset + 1))
        with open(out_path, 'w') as fh:
            writer = None
            for row in row_set:
                try:
                    if writer is None:
                        writer = DictWriter(fh, [c.column for c in row])
                        writer.writeheader()
                    data = {c.column: string_value(c.value) for c in row}
                    writer.writerow(data)
                except Exception as ex:
                    log.exception(ex)

        child_id = join_path(self.result.id, row_set.name)
        self.manager.handle_child(self.result, out_path,
                                  id=child_id,
                                  title=row_set.name,
                                  mime_type='text/csv')

    def ingest(self, file_path):
        with self.create_temp_dir() as temp_dir:
            with open(file_path, 'rb') as fh:
                _, extension = os.path.splitext(file_path)
                mime_type = self.result.mime_type
                if mime_type in self.NON_MIME_TYPES:
                    mime_type = None
                table_set = any_tableset(fh, extension=extension,
                                         mimetype=mime_type, window=20000)
                for sheet, row_set in enumerate(table_set.tables):
                    self.generate_csv(sheet, row_set, temp_dir)
