import os
import logging

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
                 emails=None, people=None, timestamp=None, headers=None):
        self.status = None
        self.id = None
        self.title = title
        self.summary = summary
        self.timestamp = timestamp
        self.author = author
        self.keywords = keywords or []
        self.emails = emails or []
        self.people = people or []
        self.file_path = file_path
        self.file_name = file_name or os.path.basename(file_path)
        self.mime_type = mime_type
        self.encoding = encoding
        self.languages = languages
        self.headers = headers
        self.error_message = None
        self.checksum = checksum
        self.size = size
        self.pages = []
        self.pdf_path = None

    @property
    def label(self):
        return self.file_name

    def emit_page(self, index, text):
        self.pages.append({'text': text, 'index': index})

    def emit_pdf_alternative(self, file_path):
        self.pdf_path = file_path

    def to_dict(self):
        return {
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
            'pages': self.pages
        }
