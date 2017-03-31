from normality import stringify

from .ingestor import Ingestor
from .support.xml import XMLSupport


class HTMLIngestor(Ingestor, XMLSupport):
    """HTML file ingestor class.

    Extracts the text from the web page.
    """

    MIME_TYPES = ['text/html']

    def configure(self):
        """Ingestor configuration."""
        self.failure_exceptions += (UnicodeDecodeError,)
        return super(HTMLIngestor, self).configure()

    def ingest(self, config):
        """Ingestor implementation."""
        body = self.fio.read()

        try:
            body = stringify(body)
        except:
            body = body
        finally:
            self.fio.seek(0)

        text, doc = self.html_to_text(body)

        self.result.title = doc.findtext('.//title')
        self.result.content = text

        for field in ['keywords', 'news_keywords', 'description']:
            value = doc.find('.//meta[@name="{}"]'.format(field))

            if value is not None:
                value = (value.get('content') or '').strip()

            self.result[field] = value
