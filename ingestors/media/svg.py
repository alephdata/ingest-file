import logging

from ingestors.base import Ingestor
from ingestors.support.html import HTMLSupport
from ingestors.support.encoding import EncodingSupport

log = logging.getLogger(__name__)


class SVGIngestor(Ingestor, EncodingSupport, HTMLSupport):
    MIME_TYPES = [
        'image/svg+xml'
    ]
    EXTENSIONS = ['svg']
    SCORE = 20

    def ingest(self, file_path):
        html_body = self.read_file_decoded(file_path)
        self.result.flag(self.result.FLAG_HTML)
        self.extract_html_content(html_body)