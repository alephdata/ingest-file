from __future__ import unicode_literals

import re
from lxml import html
from lxml.etree import ParseError, ParserError
from lxml.html.clean import Cleaner
from normality import stringify, collapse_spaces
from normality.cleaning import remove_control_chars

from ingestors.exc import ProcessingException


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

    def extract_html_text(self, doc):
        """Get all text from a DOM, also used by the XML parser."""
        text = ' '.join(self.extract_html_elements(doc))
        text = remove_control_chars(text)
        text = collapse_spaces(text)
        if len(text):
            return text

    def extract_html_elements(self, el):
        yield el.text or ' '
        for child in el:
            for text in self.extract_html_elements(child):
                yield text
        yield el.tail or ' '

    def extract_html_content(self, html_body, fix_html=True):
        """Ingestor implementation."""
        if html_body is None:
            return
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

        self.extract_html_header(doc)
        self.cleaner(doc)
        text = self.extract_html_text(doc)
        self.result.emit_html_body(html_body, text)
