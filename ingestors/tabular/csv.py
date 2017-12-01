from __future__ import unicode_literals

import io
import logging
from backports import csv
from normality import stringify
from collections import OrderedDict

from ingestors.base import Ingestor
from ingestors.support.encoding import EncodingSupport

log = logging.getLogger(__name__)


class CSVIngestor(Ingestor, EncodingSupport):
    """Decode and ingest a CSV file.

    This expects a properly formatted CSV file with a header in the first row.
    """
    MIME_TYPES = [
        'text/csv',
        'text/tsv',
        'text/tab-separated-values'
    ]
    EXTENSIONS = ['csv', 'tsv']
    SCORE = 6

    def generate_rows(self, reader, has_header=False):
        headers = next(reader) if has_header else []
        for row in reader:
            while len(headers) < len(row):
                next_col = len(headers) + 1
                headers.append('Column %s' % next_col)
            data = OrderedDict()
            for header, value in zip(headers, row):
                data[header] = stringify(value)
            yield data

    def ingest(self, file_path):
        with io.open(file_path, 'rb') as fh:
            encoding = self.detect_stream_encoding(fh)
            log.debug("Detected encoding [%s]: %s", self.result, encoding)

        with io.open(file_path, 'r', newline='', encoding=encoding) as fh:
            sample = fh.read(4096 * 10)
            fh.seek(0)

            dialect = csv.Sniffer().sniff(sample)
            # dialect.delimiter = dialect.delimiter[0]
            has_header = csv.Sniffer().has_header(sample)

            reader = csv.reader(fh, dialect=dialect)
            rows = self.generate_rows(reader, has_header=has_header)
            self.result.flag(self.result.FLAG_TABULAR)
            self.result.emit_rows(rows)
