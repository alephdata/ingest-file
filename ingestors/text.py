from normality import stringify

from ingestors.ingestor import Ingestor


class TextIngestor(Ingestor):
    """Plan text file ingestor class.

    Extracts the text from the document and enforces unicode on it.
    """

    MIME_TYPES = ['text/plain']

    def configure(self):
        """Ingestor configuration."""
        self.failure_exceptions += (UnicodeDecodeError,)
        return super(TextIngestor, self).configure()

    def ingest(self, config):
        """Ingestor implementation."""
        body = self.fio.read()

        try:
            self.result.content = stringify(body)
        except:
            self.result.content = body
        finally:
            self.fio.seek(0)
