from normality import stringify

from ingestors.ingestor import Ingestor
from ingestors.support.xml import XMLSupport


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
                value = unicode(value.get('content') or '').strip()

            if value and field in ['keywords', 'news_keywords']:
                value = map(unicode.strip, value.split(','))

            self.result[field] = value

        self.result.urls = {}

        for url, title in self.extract_links(doc):
            self.result.urls[url] = self.result.urls.get(url) or []
            self.result.urls[url].append(title)
