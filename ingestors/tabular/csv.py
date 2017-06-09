import logging
from unicodecsv import Sniffer, DictReader

from ingestors.base import Ingestor
from ingestors.support.encoding import EncodingSupport
from ingestors.exc import ProcessingException

log = logging.getLogger(__name__)


class CSVIngestor(Ingestor, EncodingSupport):
    """Decode and ingest a CSV file.

    This expects a properly formatted CSV file with a header in the first row.
    """
    MIME_TYPES = [
        'text/csv',
        'text/tab-separated-values'
    ]
    EXTENSIONS = ['csv', 'tsv']
    SCORE = 6

    def generate_rows(self, reader):
        for row in reader:
            data = {}
            for field, value in row.items():
                value = value.strip()
                if not len(value):
                    value = None
                data[field] = value
            yield data

    def ingest(self, file_path):
        with open(file_path, 'rb') as fh:
            encoding = self.detect_stream_encoding(fh)
            fh.seek(0)

            log.debug("Detected encoding [%s]: %s", self.result.label,
                      encoding)

            sniffer = Sniffer()
            sample = fh.read(4096 * 4).decode(encoding)
            if len(sample) == 0:
                raise ProcessingException("File is empty.")
            dialect = sniffer.sniff(sample.encode('utf-8'))
            fh.seek(0)

            reader = DictReader(fh, encoding=encoding, dialect=dialect)
            self.result.emit_rows(self.generate_rows(reader))
