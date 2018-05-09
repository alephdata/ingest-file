import logging
from normality import safe_filename

from ingestors.base import Ingestor
from ingestors.support.shell import ShellSupport
from ingestors.exc import ProcessingException
from ingestors.util import join_path

log = logging.getLogger(__name__)


class AccessIngestor(Ingestor, ShellSupport):
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
        try:
            output = self.subprocess.check_output([mdb_tables, local_path])
            return [
                t.strip().decode('utf-8')
                for t in output.split(b' ') if len(t.strip())
            ]
        except self.subprocess.CalledProcessError as cpe:
            log.warning("Failed to open MDB: %s", cpe)
            raise ProcessingException("Failed to extract Access database.")

    def dump_table(self, file_path, table_name, csv_path):
        mdb_export = self.find_command('mdb-export')
        args = [mdb_export, '-b', 'strip', file_path, table_name]
        with open(csv_path, 'w') as fh:
            self.subprocess.call(args, stdout=fh)
        return csv_path

    def ingest(self, file_path):
        self.result.flag(self.result.FLAG_WORKBOOK)
        for table_name in self.get_tables(file_path):
            csv_name = safe_filename(table_name, extension='csv')
            csv_path = join_path(self.work_path, csv_name)
            self.dump_table(file_path, table_name, csv_path)
            child_id = join_path(self.result.id, table_name)
            self.manager.handle_child(self.result, csv_path,
                                      id=child_id,
                                      title=table_name,
                                      file_name=csv_name,
                                      mime_type='text/csv')
