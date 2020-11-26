import logging
from followthemoney.cli.util import read_entities, read_entity
from followthemoney.util import MEGABYTE

from ingestors.ingestor import Ingestor
from ingestors.support.encoding import EncodingSupport

log = logging.getLogger(__name__)


class FtMIngestor(Ingestor, EncodingSupport):
    """Import raw FtM data into the current dataset."""

    EXTENSIONS = ["aleph", "ftm", "json"]
    SCORE = 10

    def ingest(self, file_path, entity):
        entity.set("mimeType", "application/json+ftm")
        with open(file_path, "r", encoding="utf-8") as fh:
            for idx, proxy in enumerate(read_entities(fh, cleaned=False)):
                if proxy.id is None:
                    continue
                proxy.add("proof", entity.id, quiet=True)
                self.manager.emit_entity(proxy, fragment=idx)

    @classmethod
    def match(cls, file_path, entity):
        score = super(FtMIngestor, cls).match(file_path, entity)
        if score < 1:
            return score
        try:
            with open(file_path, "rb") as fh:
                proxy = read_entity(fh, max_line=100 * MEGABYTE)
                if proxy.id is not None and proxy.schema is not None:
                    return cls.SCORE
        except Exception:
            log.exception("Failed to read FtM file: %s", entity)
        return -1
