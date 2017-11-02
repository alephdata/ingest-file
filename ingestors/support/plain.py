import logging
from normality import stringify
from normality.cleaning import remove_control_chars

log = logging.getLogger(__name__)


class PlainTextSupport(object):
    """Provides helpers for plain text context extraction."""

    def extract_plain_text_content(self, text):
        """Ingestor implementation."""
        text = stringify(text)
        if text is not None:
            text = text.strip()
            text = remove_control_chars(text)
        self.result.emit_text_body(text)
