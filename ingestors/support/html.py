import re
import logging
from lxml import html
from lxml.etree import ParseError, ParserError
from lxml.html.clean import Cleaner
from normality import stringify, collapse_spaces

from ingestors.exc import ProcessingException

log = logging.getLogger(__name__)


class HTMLSupport(object):
    """Provides helpers for HTML file context extraction."""
    # this is from lxml/apihelpers.pxi
    RE_XML_ENCODING = re.compile(ur'^(<\?xml[^>]+)\s+encoding\s*=\s*["\'][^"\']*["\'](\s*\?>|)', re.U)  # noqa

    cleaner = Cleaner(
        page_structure=True,
        scripts=True,
        javascript=True,
        style=True,
        links=True,
        embedded=True,
        forms=True,
        frames=True,
        meta=True,
        # remove_tags=['a'],
        kill_tags=['head']
    )

    def extract_html_header(self, doc):
        """Get metadata from the HTML head element."""
        if not self.result.title:
            self.result.title = stringify(doc.findtext('.//title'))
            if self.result.title:
                self.result.title = collapse_spaces(self.result.title)

        if not self.result.summary:
            description = doc.find('.//meta[@name="description"]')
            if description is not None:
                description = collapse_spaces(description.get('content'))
                self.result.summary = stringify(description)

        for field in ['keywords', 'news_keywords']:
            value = doc.find('.//meta[@name="%s"]' % field)
            if value is None:
                continue
            value = stringify(value.get('content'))
            if value is None:
                continue

            for keyword in value.split(','):
                keyword = stringify(keyword)
                if keyword is not None:
                    self.result.keywords.append(keyword)

    def pad_elements(self, el):
        if el.text is None:
            el.text = '\n'
        if el.tail is None:
            el.tail = '\n'
        for child in el:
            self.pad_elements(child)

    def extract_html_content(self, html_body, fix_html=True):
        """Ingestor implementation."""
        if html_body is None:
            self.result.emit_html_body(None, '')
        try:
            try:
                doc = html.fromstring(html_body)
            except ValueError:
                # Ship around encoding declarations.
                # https://stackoverflow.com/questions/3402520
                html_body = self.RE_XML_ENCODING.sub('', html_body, count=1)
                doc = html.fromstring(html_body)
        except (ParserError, ParseError, ValueError):
            raise ProcessingException("HTML could not be parsed.")

        print doc.findall('.//title')
        self.extract_html_header(doc)
        self.cleaner(doc)
        self.pad_elements(doc)
        text = doc.text_content()
        text = collapse_spaces(text)
        self.result.emit_html_body(html_body, text)
