from ingestors.util import decode_path, safe_string


class Result(object):

    STATUS_PENDING = u'pending'
    #: Indicates that during the processing no errors or failures occured.
    STATUS_SUCCESS = u'success'
    #: Indicates occurance of errors during the processing.
    STATUS_FAILURE = u'failure'
    #: Indicates a complete ingestor stop due to system issue.
    STATUS_STOPPED = u'stopped'

    FLAG_DIRECTORY = 'directory'
    FLAG_PACKAGE = 'package'
    FLAG_PLAINTEXT = 'plaintext'
    FLAG_TABULAR = 'tabular'
    FLAG_WORKBOOK = 'workbook'
    FLAG_IMAGE = 'image'
    FLAG_EMAIL = 'email'
    FLAG_PDF = 'pdf'
    FLAG_HTML = 'html'

    def __init__(self, **kwargs):
        self.status = None
        self.checksum = kwargs.get('checksum')
        self.size = kwargs.get('size')
        self.flags = set()
        self.file_path = decode_path(kwargs.get('file_path'))
        self.file_name = decode_path(kwargs.get('file_name'))
        self.id = kwargs.get('id')
        self.message_id = kwargs.get('message_id')
        self.title = kwargs.get('title')
        self.summary = kwargs.get('summary')
        self.mime_type = kwargs.get('mime_type')
        self.encoding = kwargs.get('encoding')
        self.date = kwargs.get('date')
        self.created_at = kwargs.get('created_at')
        self.modified_at = kwargs.get('modified_at')
        self.published_at = kwargs.get('published_at')
        self.author = kwargs.get('author')
        self.generator = kwargs.get('generator')
        self.keywords = kwargs.get('keywords') or []
        self.emails = kwargs.get('emails') or []
        self.entities = kwargs.get('entities') or []
        self.languages = kwargs.get('languages') or []
        self.ocr_languages = kwargs.get('ocr_languages', self.languages)
        self.headers = kwargs.get('headers')
        self.error_message = None
        self.pages = []
        self.body_text = None
        self.body_html = None
        self.rows = []
        self.children = []
        self.pdf_path = None

    @property
    def label(self):
        return self.file_name

    def flag(self, value):
        self.flags.add(value)

    def emit_html_body(self, html, text):
        self.body_html = safe_string(html)
        self.body_text = safe_string(text)

    def emit_text_body(self, text):
        self.body_text = safe_string(text)

    def emit_page(self, index, text):
        self.pages.append({
            'text': safe_string(text),
            'index': index
        })

    def emit_rows(self, iterator):
        for row in iterator:
            self.rows.append(row)

    def emit_pdf_alternative(self, file_path):
        self.pdf_path = safe_string(file_path)

    def emit_email(self, text):
        text = safe_string(text)
        if text is None:
            return
        self.emails.append(text)

    def emit_name(self, text):
        text = safe_string(text)
        if text is None:
            return
        self.entities.append(text)

    def emit_keyword(self, text):
        text = safe_string(text)
        if text is None:
            return
        if text not in self.keywords:
            self.keywords.append(text)

    def emit_language(self, text):
        text = safe_string(text)
        if text is None:
            return
        if text not in self.keywords:
            self.languages.append(text)

    def to_dict(self):
        return {
            'id': self.id,
            'flags': list(self.flags),
            'title': self.title,
            'message_id': self.message_id,
            'summary': self.summary,
            'keywords': self.keywords,
            'entities': self.entities,
            'emails': self.emails,
            'status': self.status,
            'file_path': self.file_path,
            'file_name': self.file_name,
            'mime_type': self.mime_type,
            'author': self.author,
            'generator': self.generator,
            'date': self.date,
            'created_at': self.created_at,
            'modified_at': self.modified_at,
            'published_at': self.published_at,
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

    def __unicode__(self):
        return safe_string(self.file_name) or self.checksum

    def __repr__(self):
        return '<Result(%s,%s)>' % (self.label, self.mime_type)
