import io
import logging
from backports import csv
from normality import safe_filename

from ingestors.support.temp import TempFileSupport
from ingestors.util import join_path

log = logging.getLogger(__name__)


class CSVEmitterSupport(TempFileSupport):
    """Generate a CSV file from a generator of rows."""

    def csv_child_iter(self, iter, name):
        with self.create_temp_dir() as temp_dir:
            out_name = safe_filename(name, extension='csv')
            out_path = join_path(temp_dir, out_name)
            row_count = 0
            with io.open(out_path, 'w', newline='', encoding='utf-8') as fh:
                writer = csv.writer(fh, quoting=csv.QUOTE_ALL)
                for row in iter:
                    writer.writerow(row)
                    row_count += 1

            log.info("Generated [%s]: %s, %s rows", name, out_name, row_count)

            child_id = join_path(self.result.id, name)
            self.manager.handle_child(self.result, out_path,
                                      id=child_id,
                                      title=name,
                                      file_name=out_name,
                                      mime_type='text/csv')
