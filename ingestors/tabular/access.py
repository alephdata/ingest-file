import os
import logging

from ingestors.base import Ingestor
from ingestors.support.temp import TempFileSupport
from ingestors.support.shell import ShellSupport

log = logging.getLogger(__name__)


class AccessIngestor(Ingestor, TempFileSupport, ShellSupport):
    MIME_TYPES = [
        'application/msaccess',
        'application/x-msaccess',
        'application/vnd.msaccess',
        'application/vnd.ms-access',
        'application/mdb',
        'application/x-mdb'
    ]
    EXTENSIONS = ['mdb']
    SCORE = 7

    def get_tables(self, local_path):
        mdb_tables = self.find_command('mdb-tables')
        output = self.subprocess.check_output([mdb_tables, local_path])
        return [t.strip() for t in output.split(' ') if len(t.strip())]

    def dump_table(self, file_path, table_name, temp_dir):
        out_path = os.path.join(temp_dir, '%s.csv' % table_name)
        mdb_export = self.find_command('mdb-export')
        args = [mdb_export, '-b', 'strip', file_path, table_name]
        with open(out_path, 'w') as fh:
            self.subprocess.call(args, stdout=fh)
        return out_path

    def ingest(self, file_path):
        with self.create_temp_dir() as temp_dir:
            for table_name in self.get_tables(file_path):
                csv_path = self.dump_table(file_path, table_name, temp_dir)
                self.manager.handle_child(self.result, csv_path,
                                          file_name=table_name,
                                          mime_type='text/csv')
