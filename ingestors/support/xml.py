from lxml import etree, html
from lxml.html.clean import Cleaner


class XMLSupport(object):
    """Provides helpers for XML parsing tasks."""

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
        doc = html.fromstring(xml)
        cleaned = self.CLEANER.clean_html(doc)
        text = unicode(cleaned.text_content())

        text = '\n'.join(map(unicode.strip, text.split('\n')))

        return text.strip(), doc

    def xml_to_text(self, xml, page_selector=None):
        parser = etree.XMLParser(recover=True, remove_comments=True)
        doc = etree.fromstring(xml, parser=parser)

        # If no page selector is set, just process the whole document
        if not page_selector:
            yield self.page_to_text(doc)
            return

        # If a page selector is set, we split the document into pages
        for page in doc.findall(page_selector):
            yield self.page_to_text(page)

    def page_to_text(self, page):
        """Extracts (PDF) page content.

        Returns the completion status, page number and the page text.
        If the status is not truthy, it requires extra processing (ex. OCR).
        """
        text = []
        completed = True
        pagenum = int(page.get('number') or 0)
        size = self.element_size(page)

        for text_element in page.findall('.//text'):
            content = text_element.xpath('string()').strip()
            if content:
                text.append(content)

        for image in page.findall('.//image'):
            ratio = self.element_size(image) / size
            if len(text) < 2 or ratio > self.IMAGE_RATIO_FOR_OCR:
                completed = False

        text = '\n'.join(text).strip()

        self.logger.debug(
            'Extracted %d characters from page %r.', len(text), pagenum)

        return completed, pagenum, text

    def element_size(self, el):
        width = float(el.attrib.get('width', 1))
        height = float(el.attrib.get('height', 1))
        return width * height
