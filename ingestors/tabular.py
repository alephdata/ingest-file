from .ingestor import Ingestor
from .support.office import OfficeSupport


class TabularIngestor(Ingestor, OfficeSupport):
    """Tabular document (csv, excel, etc.) ingestor class.

    Converts the document into sheets and rows.
    """

    MIME_TYPES = [
        'text/csv',
        'text/tsv',
        'text/tab-separated-values',
        'text/comma-separated-values',
        'application/csv',
        'application/tsv',
        'application/xls',
        'application/excel',
        'application/x-excel',
        'application/ms-excel',
        'application/x-msexcel',
        'application/vnd.ms-excel',
        'application/vnd.oasis.opendocument.spreadsheet',
        'application/x-vnd.oasis.opendocument.spreadsheet',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheetapplication/zip',  # noqa
    ]

    def configure(self):
        """Ingestor configuration."""
        config = super(TabularIngestor, self).configure()
        return config

    def ingest(self, config):
        """Ingestor implementation."""
        count = 0
        self.result.columns = dict()

        tableset = self.tabular_to_tableset(
            self.fio, self.file_path, self.result.mime_type, config)

        for sheet_number, rowset in enumerate(tableset):
            self.result.columns[rowset.name] = False

            for mapping in self.sheet_row_to_dicts(sheet_number, rowset):
                self.detach(
                    ingestor_class=Ingestor,
                    fio=None,
                    file_path=self.file_path,
                    result_extra={
                        'sheet_name': rowset.name,
                        'sheet_number': sheet_number,
                        'order': count,
                        'content': mapping,
                    }
                )

                if not self.result.columns.get(rowset.name):
                    self.result.columns[rowset.name] = mapping.keys()

                count += 1
