import os
import logging

from ingestors.util import decode_path

log = logging.getLogger(__name__)


class Result(object):

    #: Indicates that during the processing no errors or failures occured.
    STATUS_SUCCESS = u'success'
    #: Indicates occurance of errors during the processing.
    STATUS_FAILURE = u'failure'
    #: Indicates a complete ingestor stop due to system issue.
    STATUS_STOPPED = u'stopped'

    def __init__(self, id=None, title=None, file_path=None, file_name=None,
                 mime_type=None, checksum=None, size=None, encoding=None,
                 summary=None, keywords=None, languages=[], author=None,
                 emails=None, entities=None, timestamp=None, headers=None):
        self.status = None
        self.file_path = decode_path(file_path)
        file_name = file_name or os.path.basename(self.file_path)
        self.file_name = decode_path(file_name)
        self.id = id or self.file_path
        self.title = title
        self.summary = summary
        self.timestamp = timestamp
        self.author = author
        self.keywords = keywords or []
        self.emails = emails or []
        self.entities = entities or []
        self.mime_type = mime_type
        self.encoding = encoding
        self.languages = languages
        self.headers = headers
        self.error_message = None
        self.checksum = checksum
        self.size = size
        self.pages = []
        self.body_text = None
        self.body_html = None
        self.rows = []
        self.children = []
        self.pdf_path = None

    @property
    def label(self):
        return self.file_name

    def emit_html_body(self, html, text):
        self.body_html = html
        self.body_text = text

    def emit_text_body(self, text):
        self.body_text = text

    def emit_page(self, index, text):
        self.pages.append({'text': text, 'index': index})

    def emit_rows(self, iterator):
        for row in iterator:
            self.rows.append(row)

    def emit_pdf_alternative(self, file_path):
        self.pdf_path = file_path

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'summary': self.summary,
            'keywords': self.keywords,
            'status': self.status,
            'file_path': self.file_path,
            'file_name': self.file_name,
            'mime_type': self.mime_type,
            'error_message': self.error_message,
            'checksum': self.checksum,
            'pdf_path': self.pdf_path,
            'size': self.size,
            'pages': self.pages,
            'rows': self.rows,
            'body_text': self.body_text,
            'body_html': self.body_html,
            'children': [c.to_dict() for c in self.children]
        }

    def __repr__(self):
        return '<Result(%s,%s)>' % (self.label, self.mime_type)
