from ingestors.exc import ProcessingException


class PlainTextSupport(object):
    """Provides helpers for plain text context extraction."""

    def extract_plain_text_content(self, entity, text):
        """Ingestor implementation."""
        try:
            if isinstance(text, str):
                text.encode('utf-8')
            entity.set('bodyText', text)
        except (UnicodeDecodeError, UnicodeEncodeError) as ue:
            raise ProcessingException('Cannot decode text: %s' % ue)
