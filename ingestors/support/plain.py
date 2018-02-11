import six
from normality import stringify

from ingestors.exc import ProcessingException


class PlainTextSupport(object):
    """Provides helpers for plain text context extraction."""

    def extract_plain_text_content(self, text):
        """Ingestor implementation."""
        if text is None:
            self.result.emit_text_body(None)

        try:
            if not isinstance(text, six.text_type):
                text = stringify(text)
            text.encode('utf-8')
            self.result.emit_text_body(text)
        except (UnicodeDecodeError, UnicodeEncodeError) as ue:
            raise ProcessingException('Invalid file encoding: %s' % ue)
