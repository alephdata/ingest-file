from normality import stringify

from .ingestor import Ingestor


class TextIngestor(Ingestor):
    """Plan text file ingestor class.

    Extracts the text from the document and enforces unicode on it.
    """

    MIME_TYPES = ['text/plain']

    def configure(self):
        """Ingestor configuration."""
        self.failure_exceptions += (UnicodeDecodeError,)
        return super(TextIngestor, self).configure()

    def ingest(self, original, transformed, config):
        """Ingestor implementation."""
        body = original.read()

        try:
            return stringify(body)
        except:
            return body
        finally:
            self.fio.seek(0)
