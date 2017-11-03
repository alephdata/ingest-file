import rfc822
from time import mktime
from olefile import isOleFile
from datetime import datetime
from normality import safe_filename
from flanker.addresslib import address

from ingestors.base import Ingestor
from ingestors.support.temp import TempFileSupport
from ingestors.support.plain import PlainTextSupport
from ingestors.email.outlookmsg_lib import Message
from ingestors.util import string_value, join_path


class OutlookMsgIngestor(Ingestor, TempFileSupport, PlainTextSupport):
    MIME_TYPES = []
    EXTENSIONS = ['msg']
    SCORE = 10

    def ingest_attachment(self, attached, temp_dir):
        name = attached.longFilename or attached.shortFilename
        file_path = safe_filename(name, default='attachment')
        file_path = join_path(temp_dir, safe_filename(name))
        with open(file_path, 'w') as fh:
            if attached.data is not None:
                fh.write(attached.data)
        self.manager.handle_child(self.result, file_path,
                                  id=join_path(self.result.id, name),
                                  title=name,
                                  file_name=name,
                                  mime_type=attached.mimeType)

    def parse_headers(self, headers):
        self.result.title = headers.get('Subject')

        if headers.get('Message-Id') and self.result.id is None:
            self.result.id = headers.get('Message-Id')

        if headers.get('From'):
            addr = address.parse(headers.get('From'))
            if addr is not None:
                if addr.display_name and addr.display_name != addr.address:
                    self.result.author = addr.display_name
                    self.result.entities.append(addr.display_name)
                self.result.emails.append(addr.address)

        for hdr in ['To', 'CC', 'BCC']:
            if headers.get(hdr):
                for addr in address.parse_list(headers.get(hdr)):
                    if addr.display_name and addr.display_name != addr.address:
                        self.result.entities.append(addr.display_name)
                    self.result.emails.append(addr.address)

        date = headers.get('Date')
        date = rfc822.parsedate(date)
        if date is not None:
            self.result.timestamp = datetime.fromtimestamp(mktime(date))

        self.result.headers = dict([(k, string_value(v)) for k, v in
                                    headers.items()])

    def ingest(self, file_path):
        with self.create_temp_dir() as temp_dir:
            message = Message(file_path)
            if message.header is not None:
                self.parse_headers(message.header)

            self.extract_plain_text_content(message.body)
            for attachment in message.attachments:
                self.ingest_attachment(attachment, temp_dir)

    @classmethod
    def match(cls, file_path, mime_type=None):
        if isOleFile(file_path):
            return super(OutlookMsgIngestor, cls).match(file_path,
                                                        mime_type=mime_type)
        return -1
