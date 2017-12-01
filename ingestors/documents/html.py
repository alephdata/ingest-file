from ingestors.base import Ingestor
from ingestors.support.html import HTMLSupport
from ingestors.support.encoding import EncodingSupport


class HTMLIngestor(Ingestor, EncodingSupport, HTMLSupport):
    "HTML file ingestor class. Extracts the text from the web page."

    MIME_TYPES = ['text/html']

    def ingest(self, file_path):
        """Ingestor implementation."""
        html_body = self.read_file_decoded(file_path)
        self.result.flag(self.result.FLAG_HTML)
        self.extract_html_content(html_body)
