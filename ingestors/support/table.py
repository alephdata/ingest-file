import logging
from followthemoney.types import registry

log = logging.getLogger(__name__)


class TableSupport(object):
    """Handle creating rows from an ingestor."""

    def emit_row_dicts(self, table, rows):
        for index, row in enumerate(rows, 1):
            values = list(row.values())
            entity = self.manager.make_entity('Row')
            entity.make_id(table.id, index)
            entity.set('index', index)
            entity.set('cells', registry.json.pack(values))
            entity.set('table', table)
            self.manager.emit_entity(entity)
            self.manager.emit_text_fragment(table, values, index)

    def emit_row_tuples(self, table, rows):
        for index, row in enumerate(rows, 1):
            row = list(row)
            entity = self.manager.make_entity('Row')
            entity.make_id(table.id, index)
            entity.set('index', index)
            entity.add('cells', registry.json.pack(row))
            entity.add('table', table)
            self.manager.emit_entity(entity)
            self.manager.emit_text_fragment(table, row, index)
