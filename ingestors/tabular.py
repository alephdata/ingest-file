from .ingestor import Ingestor
from .support.office import OfficeSupport


class TabularIngestor(Ingestor, OfficeSupport):
    """Tabular document (csv, excel, etc.) ingestor class.

    Converts the document into sheets and rows.
    """

    MIME_TYPES = [
        'text/csv',
        'application/excel',
        'application/x-excel',
        'application/x-msexcel',
        'application/vnd.ms-excel',
        'text/tab-separated-values',
        'application/vnd.oasis.opendocument.spreadsheet',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ]

    def configure(self):
        """Ingestor configuration."""
        config = super(TabularIngestor, self).configure()
        return config

    def ingest(self, config):
        """Ingestor implementation."""
        tableset = self.tabular_to_tableset(
            self.fio, self.file_path, self.result.mime_type, config)

        self.result.columns = dict()
        count = 0

        for sheet_number, rowset in enumerate(tableset):
            self.result.columns[rowset.name] = False

            for mapping in self.sheet_row_to_dicts(sheet_number, rowset):
                row_ingestor = Ingestor(self.fio, self.file_path, self)
                row_ingestor.result.sheet_name = rowset.name
                row_ingestor.result.sheet_number = sheet_number
                row_ingestor.result.page = count
                row_ingestor.result.content = mapping

                self.children.append(row_ingestor)

                if not self.result.columns.get(rowset.name):
                    self.result.columns[rowset.name] = mapping.keys()

                count += 1
