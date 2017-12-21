from __future__ import unicode_literals

import logging
from olefile import isOleFile
from normality import stringify
from email.parser import Parser

from ingestors.base import Ingestor
from ingestors.support.email import EmailSupport
from ingestors.support.ole import OLESupport
from ingestors.email.outlookmsg_lib import Message

log = logging.getLogger(__name__)


class OutlookMsgIngestor(Ingestor, EmailSupport, OLESupport):
    MIME_TYPES = [
        'appliation/msg',
        'appliation/x-msg',
        'message/rfc822'
    ]
    EXTENSIONS = ['msg']
    SCORE = 10

    def _parse_headers(self, message):
        headers = message.getField('007D')
        try:
            assert headers is not None
            message = Parser().parsestr(headers, headersonly=True)
            self.extract_headers_metadata(message.items())
        except Exception as exc:
            log.warning("Cannot parse Outlook headers: %s" % exc)
            self.result.headers = {
                'Subject': message.getField('0037'),
                'BCC': message.getField('0E02'),
                'CC': message.getField('0E03'),
                'To': message.getField('0E04'),
                'From': message.getField('1046'),
                'Message-ID': message.getField('1035'),
            }

    def ingest(self, file_path):
        message = Message(file_path)
        self._parse_headers(message)
        self.extract_plain_text_content(message.getField('1000'))
        # WARNING: this is fuck-stupid, destroys incremental import:
        # self.update('id', message.getField('1035'))
        self.update('title', message.getField('0037'))
        self.update('title', message.getField('0070'))
        self.update('author', message.getField('0C1A'))

        # all associated person names, i.e. sender, recipient etc.
        for field in ('0C1A', '0E04', '0040'):
            value = message.getField(field)
            self.result.entities.append(value)

        # fields storing emails:
        for field in ('0C1F', '0076', '0078'):
            value = message.getField(field)
            self.result.emails.append(value)

        # from pprint import pprint
        # pprint(self.result.to_dict())

        self.extract_olefileio_metadata(message)
        self.result.flag(self.result.FLAG_EMAIL)
        self.result.flag(self.result.FLAG_PLAINTEXT)
        with self.create_temp_dir() as temp_dir:
            for attachment in message.attachments:
                name = stringify(attachment.longFilename)
                name = name or stringify(attachment.shortFilename)
                self.ingest_attachment(name,
                                       attachment.mimeType,
                                       attachment.data,
                                       temp_dir)

    @classmethod
    def match(cls, file_path, result=None):
        if isOleFile(file_path):
            return super(OutlookMsgIngestor, cls).match(file_path,
                                                        result=result)
        return -1
