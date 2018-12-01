import io
import csv
import logging
from collections import OrderedDict
from followthemoney import model

from ingestors.ingestor import Ingestor
from ingestors.support.encoding import EncodingSupport
from ingestors.exc import ProcessingException
from ingestors.util import safe_string

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
    SCORE = 7

    def generate_rows(self, entity, reader, has_header=False):
        headers = next(reader) if has_header else []
        headers = [safe_string(h) for h in headers]
        for idx, row in enumerate(reader, 1):
            while len(headers) < len(row):
                next_col = len(headers) + 1
                headers.append('Column %s' % next_col)

            row = self.manager.make_entity('Row')
            row.make_id(entity.id, idx)
            row.set('table', entity)
            row.set('index', idx)
            for header, value in zip(headers, row):
                # FIXME: How on earth will this work???
                row.add('cell', safe_string(value))
            self.manager.emit_entity(row)

    def ingest(self, file_path, entity):
        entity.schema = model.get('Table')
        with io.open(file_path, 'rb') as fh:
            encoding = self.detect_stream_encoding(fh)
            log.debug("Detected encoding [%s]: %s", entity, encoding)

        fh = io.open(file_path, 'r', encoding=encoding, errors='replace')
        try:
            sample = fh.read(4096 * 10)
            fh.seek(0)

            dialect = csv.Sniffer().sniff(sample)
            # dialect.delimiter = dialect.delimiter[0]
            has_header = csv.Sniffer().has_header(sample)

            reader = csv.reader(fh, dialect=dialect)
            self.generate_rows(entity, reader, has_header=has_header)
        except UnicodeDecodeError as ude:
            log.warning("Encoding error: %s", self.result)
            raise ProcessingException("Could not decode CSV (%s)" % encoding)
        except Exception as err:
            log.exception("CSV error: %s", err)
            raise ProcessingException("Invalid CSV: %s" % err)
        finally:
            fh.close()
