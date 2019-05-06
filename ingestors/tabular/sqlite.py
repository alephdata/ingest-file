import logging
import sqlite3
from followthemoney import model
from collections import OrderedDict

from ingestors.ingestor import Ingestor
from ingestors.support.table import TableSupport
from ingestors.exc import ProcessingException

log = logging.getLogger(__name__)


class SQLiteIngestor(Ingestor, TableSupport):
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
        try:
            cur.execute("SELECT * FROM %s;" % table)
        except sqlite3.OperationalError as oe:
            log.warning("SQLite error: %s", oe)
            raise ProcessingException("Cannot query table: %s" % table)

        headers = [i[0] for i in cur.description]
        while True:
            try:
                row = cur.fetchone()
                if row is None:
                    return
                data = OrderedDict()
                for header, value in zip(headers, row):
                    data[header] = value
                yield data
            except sqlite3.OperationalError as oe:
                log.warning("SQLite error: %s", oe)

    def ingest(self, file_path, entity):
        entity.schema = model.get('Workbook')
        conn = sqlite3.connect(file_path)
        try:
            for table_name in self.get_tables(conn):
                table = self.manager.make_entity('Table', parent=entity)
                table.make_id(entity, table_name)
                table.set('title', table_name)
                rows = self.generate_rows(conn, table_name)
                self.emit_row_dicts(table, rows)
                self.manager.emit_entity(table)
        finally:
            conn.close()

    @classmethod
    def match(cls, file_path, entity):
        score = super(SQLiteIngestor, cls).match(file_path, entity)
        if score > 0:
            try:
                conn = sqlite3.connect(file_path)
                conn.execute("SELECT * FROM sqlite_master;").fetchall()
                return score
            except Exception:
                pass
        return -1
