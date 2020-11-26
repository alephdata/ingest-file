import json

from followthemoney import model
from followthemoney.util import MEGABYTE

from ingestors.ingestor import Ingestor
from ingestors.support.encoding import EncodingSupport
from ingestors.exc import ProcessingException


class JSONIngestor(Ingestor, EncodingSupport):

    MIME_TYPES = [
        "application/json",
        "text/javascript",
    ]
    EXTENSIONS = ["json"]
    MAX_SIZE = 100 * MEGABYTE
    SCORE = 3

    def _collect_text(self, obj):
        if isinstance(obj, (list, set, tuple)):
            for item in obj:
                yield from self._collect_text(item)
        if isinstance(obj, dict):
            for item in obj.values():
                yield from self._collect_text(item)
        if isinstance(obj, str):
            yield obj

    def ingest(self, file_path, entity):
        for file_size in entity.get("fileSize"):
            if int(file_size) > self.MAX_SIZE:
                raise ProcessingException("JSON file is too large.")

        with open(file_path, "rb") as fh:
            encoding = self.detect_stream_encoding(fh)

        with open(file_path, "r", encoding=encoding) as fh:
            try:
                data = json.load(fh)
                for idx, text in enumerate(self._collect_text(data)):
                    self.manager.emit_text_fragment(entity, [text], idx)
            except Exception as exc:
                raise ProcessingException("Cannot parse JSON file: %s" % exc) from exc
