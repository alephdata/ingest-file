import tempfile

import unicodecsv as csv

from .ingestor import Ingestor
from .support.office import OfficeSupport


class TabularSheetIngestor(Ingestor, OfficeSupport):
    """Tabular document (csv, tsv) ingestor.

    This ingestor handles basic tabular documents.
    There's a separate ingestor to handle more complex sheet-based formats.
    """
    MIME_TYPES = [
        'text/csv',
        'text/tsv',
        'text/tab-separated-values',
        'text/comma-separated-values',
        'application/csv',
        'application/tsv'
    ]

    def ingest(self, config):
        """Ingestor implementation."""
        tableset = self.tabular_to_tableset(
            self.fio, self.file_path, self.result.mime_type, config)

        assert len(tableset) == 1, 'More than one sheets in this document.'

        rowset = tableset[0]

        self.result.content = []
        self.result.columns = []
        self.result.sheet_name = self.result.get('sheet_name') or 'table'
        self.result.sheet_number = self.result.get('sheet_number') or 0

        for row_dict in self.rowset_to_dicts(rowset):
            self.result.content.append(row_dict)

            if not self.result.columns:
                self.result.columns = row_dict.keys()


class TabularIngestor(TabularSheetIngestor):
    """Tabular document (excel, etc.) ingestor class.

    Splits complex tabular documents and feeds them to a sheet-based ingestor.
    """

    MIME_TYPES = [
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

    def ingest(self, config):
        """Ingestor implementation."""
        tableset = self.tabular_to_tableset(
            self.fio, self.file_path, self.result.mime_type, config)

        # If this is a one sheet document, crunch it
        if len(tableset) == 1:
            self.fio.seek(0)
            return super(TabularIngestor, self).ingest(config)

        # If this is a complex document, split the workload
        count = 0
        self.result.columns = []
        for sheet_number, rowset in enumerate(tableset):
            sheet_path = '{}_sheet-{}.csv'.format(self.file_path, count)

            with tempfile.NamedTemporaryFile(mode='rb+') as sheetfio:
                rows = self.rowset_to_dicts(rowset)
                sheet_writer = csv.writer(sheetfio)
                columns = None

                for row in rows:
                    if not columns:
                        columns = row.keys()
                        sheet_writer.writerow(columns)

                    sheet_writer.writerow(row.values())

                sheetfio.seek(0)

                self.detach(
                    fio=sheetfio,
                    file_path=sheet_path,
                    ingestor_class=TabularSheetIngestor,
                    mime_type=TabularSheetIngestor.MIME_TYPES[0],
                    extra={
                        'sheet_name': rowset.name,
                        'sheet_number': sheet_number,
                        'order': count,
                    }
                )

            count += 1
