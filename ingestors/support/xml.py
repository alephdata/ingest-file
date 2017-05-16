import logging

try:
    from lxml import etree, html
    from lxml.html.clean import Cleaner
except ImportError as error:
    logging.exception(error)

    def Cleaner(*args, **kwargs):
        pass


class XMLSupport(object):
    """Provides helpers for XML parsing tasks."""

    logger = logging.getLogger(__name__)

    #: Image ratio compared to the document size
    IMAGE_RATIO_FOR_OCR = 0.3

    CLEANER = Cleaner(
        scripts=True,
        javascript=True,
        style=True,
        links=True,
        embedded=True,
        forms=True,
        frames=True,
        annoying_tags=True,
        meta=True,
        remove_tags=['a'],
        kill_tags=['head']
    )

    def html_to_text(self, xml):
        if not xml:
            return None, etree.Element('empty')

        doc = html.fromstring(xml)
        cleaned = self.CLEANER.clean_html(doc)
        text = unicode(cleaned.text_content())

        text = '\n'.join(map(unicode.strip, text.split('\n')))

        return text.strip(), doc

    def xml_to_pages(self, xml, page_selector):
        parser = etree.XMLParser(recover=True, remove_comments=True)
        doc = etree.fromstring(xml, parser=parser)

        # If a page selector is set, we split the document into pages
        for page in doc.findall(page_selector):
            yield page

    def page_to_text(self, page):
        """Extracts (PDF converted to XML) page content.

        Returns the completion status, page number and the page text.
        If the status is not truthy, it requires extra processing (ex. OCR).
        """
        text = []
        needs_ocr = False
        size = self.element_size(page)

        for text_element in page.findall('.//text'):
            content = text_element.xpath('string()').strip()
            if content:
                text.append(content)

        for image in page.findall('.//image'):
            ratio = self.element_size(image) / size
            if len(text) < 2 or ratio > self.IMAGE_RATIO_FOR_OCR:
                needs_ocr = True

        text = u'\n'.join(text).strip()

        self.logger.debug(
            'Extracted %d characters from page %r.',
            len(text), page.get('number')
        )

        return needs_ocr, text

    def element_size(self, el):
        width = float(el.attrib.get('width', 1))
        height = float(el.attrib.get('height', 1))
        return width * height

    def extract_links(self, tree):
        """Extracts and embeds URLs from links."""
        for link in tree.findall('.//a'):
            yield link.get('href'), link.text
