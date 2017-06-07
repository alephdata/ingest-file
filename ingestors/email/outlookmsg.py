import os
import rfc822
import logging
from time import mktime
from datetime import datetime

from olefile import isOleFile
from flanker.addresslib import address

from ingestors.base import Ingestor
from ingestors.documents.plain import PlainTextIngestor
from ingestors.support.temp import TempFileSupport
from ingestors.email.outlookmsg_lib import Message
from ingestors.util import string_value


log = logging.getLogger(__name__)


class OutlookMsgIngestor(Ingestor, TempFileSupport):
    MIME_TYPES = []
    EXTENSIONS = ['msg']
    SCORE = 10

    def ingest_attachment(self, attachment, temp_dir):
        try:
            name = attachment.longFilename or attachment.shortFilename
            if name is None:
                name = 'attachment'

            if attachment.data is None:
                log.warning("Attachment is empty: %s", name)
                return

            file_path = os.path.join(temp_dir, name)
            with open(file_path, 'w') as fh:
                fh.write(attachment.data)
            self.manager.handle_child(self.result, file_path)
        except Exception as ex:
            log.exception(ex)

    def parse_headers(self, headers):
        self.result.title = headers.get('Subject')

        if headers.get('Message-Id'):
            self.result.id = headers.get('Message-Id')

        if headers.get('From'):
            addr = address.parse(headers.get('From'))
            if addr is not None:
                if addr.display_name:
                    self.result.author = addr.display_name
                    self.result.people.append(addr.display_name)
                self.result.emails.append(addr.address)

        for hdr in ['To', 'CC', 'BCC']:
            if headers.get(hdr):
                for addr in address.parse_list(headers.get(hdr)):
                    if addr.display_name:
                        self.result.people.append(addr.display_name)
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

            for attachment in message.attachments:
                self.ingest_attachment(attachment, temp_dir)

            if message.body is not None:
                body_path = os.path.join(temp_dir, 'body.txt')
                with open(body_path, 'w') as fh:
                    fh.write(message.body.encode('utf-8'))
                self.manager.delegate(PlainTextIngestor, self.result,
                                      body_path)

    @classmethod
    def match(cls, file_path, mime_type=None):
        if isOleFile(file_path):
            return super(OutlookMsgIngestor, cls).match(file_path,
                                                        mime_type=mime_type)
        return -1
