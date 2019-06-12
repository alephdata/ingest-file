import logging
import csv
from pathlib import Path
from followthemoney.types import registry

log = logging.getLogger(__name__)


class TableSupport(object):
    """Handle creating rows from an ingestor."""

    def emit_row_dicts(self, table, rows):
        csv_path = Path(self.manager.work_path).joinpath(table.id + ".csv")
        with open(csv_path, 'w', encoding='utf-8') as fp:
            csv_writer = csv.writer(fp)
            for index, row in enumerate(rows, 1):
                values = list(row.values())
                csv_writer.writerow(values)
                entity = self.manager.make_entity('Row')
                entity.make_id(table.id, index)
                entity.set('index', index)
                entity.set('cells', registry.json.pack(values))
                entity.set('table', table)
                self.manager.emit_entity(entity)
                self.manager.emit_text_fragment(table, values, entity.id)
        csv_hash = self.manager.archive_store(csv_path)
        table.set("csvHash", csv_hash)

    def emit_row_tuples(self, table, rows):
        csv_path = Path(self.manager.work_path).joinpath(table.id + ".csv")
        with open(csv_path, 'w', encoding='utf-8') as fp:
            csv_writer = csv.writer(fp)
            for index, row in enumerate(rows, 1):
                row = list(row)
                csv_writer.writerow(row)
                entity = self.manager.make_entity('Row')
                entity.make_id(table.id, index)
                entity.set('index', index)
                entity.add('cells', registry.json.pack(row))
                entity.add('table', table)
                self.manager.emit_entity(entity)
                self.manager.emit_text_fragment(table, row, entity.id)
        csv_hash = self.manager.archive_store(csv_path)
        table.set("csvHash", csv_hash)
