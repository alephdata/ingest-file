import os
from lxml import html
from lxml.html.clean import Cleaner
from normality import stringify, collapse_spaces

from ingestors.base import Ingestor
from ingestors.support.encoding import EncodingSupport
from ingestors.support.pdf import PDFSupport


class HTMLIngestor(Ingestor, EncodingSupport, PDFSupport):
    "HTML file ingestor class. Extracts the text from the web page."

    MIME_TYPES = ['text/html']

    cleaner = Cleaner(
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
        # kill_tags=['head']
    )

    def render_html_to_pdf(self, html_path, temp_dir):
        """OK, this is weirder. Converting HTML to PDF via WebKit."""
        pdf_path = os.path.join(temp_dir, 'page.pdf')
        self.exec_command('wkhtmltopdf',
                          '--disable-javascript',
                          '--no-outline',
                          '--no-images',
                          '--lowquality',
                          '--quiet',
                          '--disable-forms',
                          '--disable-local-file-access',
                          '--load-error-handling',
                          'skip',
                          html_path,
                          pdf_path)
        self.assert_outfile(pdf_path)
        return pdf_path

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

    # def extract_links(self, tree):
    #     """Extracts and embeds URLs from links."""
    #     for link in tree.findall('.//a'):
    #         yield link.get('href'), link.text

    def ingest(self, file_path):
        """Ingestor implementation."""
        body = self.read_file_decoded(file_path)
        doc = html.fromstring(body)
        self.extract_html_header(doc)
        self.cleaner(doc)

        with self.create_temp_dir() as temp_dir:
            html_path = os.path.join(temp_dir, 'page.html')
            with open(html_path, 'w') as fh:
                data = html.tostring(doc, pretty_print=True)
                fh.write(data)
            pdf_path = self.render_html_to_pdf(html_path, temp_dir)
            self.pdf_alternative_extract(pdf_path)
