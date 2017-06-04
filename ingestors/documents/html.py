# from normality import stringify

from ingestors.base import Ingestor


class HTMLIngestor(Ingestor):
    """HTML file ingestor class.

    Extracts the text from the web page.
    """

    MIME_TYPES = ['text/html']

    def ingest(self, file_path):
        """Ingestor implementation."""
        # with open(file_path, 'r') as fh:
        #     print fh.read()
