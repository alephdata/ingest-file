import logging
import sqlite3

from ingestors.base import Ingestor
from ingestors.support.csv import CSVEmitterSupport

log = logging.getLogger(__name__)


class SQLiteIngestor(Ingestor, CSVEmitterSupport):
    MIME_TYPES = [
        'application/x-sqlite3',
        'application/x-sqlite',
        'application/sqlite3',
        'application/sqlite',
    ]
    EXTENSIONS = ['sqlite3', 'sqlite', 'db']
    SCORE = 8

    def get_tables(self, conn):
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type = 'table';")
        for (name,) in c.fetchall():
            yield name

    def generate_rows(self, conn, table):
        cur = conn.cursor()
        # FIXME make this a parameter somehow.
        cur.execute("SELECT * FROM %s;" % table)
        yield [i[0] for i in cur.description]
        while True:
            rows = cur.fetchmany()
            if not len(rows):
                return
            for row in rows:
                yield list(row)

    def ingest(self, file_path):
        self.result.flag(self.result.FLAG_WORKBOOK)
        conn = sqlite3.connect(file_path)
        try:
            for table_name in self.get_tables(conn):
                rows = self.generate_rows(conn, table_name)
                self.csv_child_iter(rows, table_name)
        finally:
            conn.close()

    @classmethod
    def match(cls, file_path, result=None):
        score = super(SQLiteIngestor, cls).match(file_path, result=result)  # noqa
        if score > 0:
            try:
                conn = sqlite3.connect(file_path)
                conn.execute("SELECT * FROM sqlite_master;").fetchall()
                return score
            except Exception:
                pass
        return -1
