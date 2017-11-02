import logging
from normality import stringify

log = logging.getLogger(__name__)


class PlainTextSupport(object):
    """Provides helpers for plain text context extraction."""

    def extract_plain_text_content(self, text):
        """Ingestor implementation."""
        text = stringify(text)
        if text is not None:
            text = text.strip()
        self.result.emit_text_body(text)
