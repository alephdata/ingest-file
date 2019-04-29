import logging
# from banal import ensure_list

log = logging.getLogger(__name__)


class TableSupport(object):
    """Handle creating rows from an ingestor."""

    def emit_row_dicts(self, table, rows, workbook=None):
        for index, row in enumerate(rows, 1):
            entity = self.manager.make_entity('Row')
            entity.make_id(table.id, index)
            entity.set('index', index)
            entity.set('cells', list(row.values()))
            entity.set('table', table)
            table_fragment = self.manager.make_entity('Document')
            table_fragment.id = table.id
            table_fragment.set('indexText', ', '.join(row.values()))
            self.manager.emit_entity(entity)
            self.manager.emit_entity(table_fragment, fragment=str(index))
            if workbook:
                workbook_fragment = self.manager.make_entity('Document')
                workbook_fragment.id = workbook.id
                workbook_fragment.set('indexText', ', '.join(row))
                self.manager.emit_entity(workbook_fragment, fragment=str(index))  # noqa

    def emit_row_tuples(self, table, rows, workbook=None):
        for index, row in enumerate(rows, 1):
            entity = self.manager.make_entity('Row')
            entity.make_id(table.id, index)
            entity.set('index', index)
            entity.add('cells', list(row))
            entity.add('table', table)
            table_fragment = self.manager.make_entity('Document')
            table_fragment.id = table.id
            table_fragment.set('indexText', ', '.join(row))
            self.manager.emit_entity(entity)
            self.manager.emit_entity(table_fragment, fragment=str(index))
            if workbook:
                workbook_fragment = self.manager.make_entity('Document')
                workbook_fragment.id = workbook.id
                workbook_fragment.set('indexText', ', '.join(row))
                self.manager.emit_entity(workbook_fragment, fragment=str(index))  # noqa
