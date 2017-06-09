import logging

from ingestors.base import Ingestor
from ingestors.support.temp import TempFileSupport
from ingestors.support.shell import ShellSupport
from ingestors.util import make_filename, join_path

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
        out_file = make_filename(table_name, extension='csv')
        out_file = join_path(temp_dir, out_file)
        mdb_export = self.find_command('mdb-export')
        args = [mdb_export, '-b', 'strip', file_path, table_name]
        with open(out_file, 'w') as fh:
            self.subprocess.call(args, stdout=fh)
        return out_file

    def ingest(self, file_path):
        with self.create_temp_dir() as temp_dir:
            for table_name in self.get_tables(file_path):
                csv_path = self.dump_table(file_path, table_name, temp_dir)
                child_id = join_path(self.result.id, table_name)
                self.manager.handle_child(self.result, csv_path,
                                          id=child_id,
                                          title=table_name,
                                          mime_type='text/csv')
