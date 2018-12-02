import logging
# from banal import ensure_list

log = logging.getLogger(__name__)


class TableSupport(object):
    """Handle creating rows from an ingestor."""

    def emit_row_dicts(self, table, rows):
        for index, row in enumerate(rows, 1):
            entity = self.manager.make_entity('Row')
            entity.make_id(table.id, index)
            entity.set('index', index)
            entity.add('cells', list(row.values()))
            entity.add('table', table)
            self.manager.emit_entity(entity)

    def emit_row_tuples(self, table, rows):
        for index, row in enumerate(rows, 1):
            entity = self.manager.make_entity('Row')
            entity.make_id(table.id, index)
            entity.set('index', index)
            entity.add('cells', list(row))
            entity.add('table', table)
            self.manager.emit_entity(entity)
