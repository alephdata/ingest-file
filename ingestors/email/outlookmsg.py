from __future__ import unicode_literals

import logging
from flanker import mime
from olefile import isOleFile
from flanker.mime.message.errors import DecodingError

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

    def _parse_headers(self, headers):
        if headers is None:
            return
        try:
            first, rest = headers.split('\r\n', 1)
            if ':' not in first:
                headers = rest
            msg = mime.from_string(headers.encode('utf-8'))
            self.extract_headers_metadata(msg.headers)
        except DecodingError as derr:
            log.warning("Cannot parse Outlook headers: %s" & derr)

    def ingest(self, file_path):
        message = Message(file_path)
        self._parse_headers(message.getField('007D'))
        self.extract_plain_text_content(message.getField('1000'))
        self.update('id', message.getField('1035'))
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
        with self.create_temp_dir() as temp_dir:
            for attachment in message.attachments:
                name = attachment.longFilename or attachment.shortFilename
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
