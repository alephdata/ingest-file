
from .ingestor import Ingestor
from .support.encoding import EncodingSupport


class TextIngestor(Ingestor, EncodingSupport):
    """Plan text file ingestor class.

    Extracts the text from the document and enforces unicode on it.
    """

    MIME_TYPES = ['text/plain']

    def configure(self):
        """Ingestor configuration."""
        self.failure_exceptions += (UnicodeDecodeError,)
        return {}

    def ingest(self, config):
        """Ingestor implementation."""
        encoding = self.detect_encoding(self.fio)
        body = self.fio.read()

        try:
            return body.decode(encoding)
        except:
            return body
        finally:
            self.fio.seek(0)
