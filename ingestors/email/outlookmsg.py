from __future__ import unicode_literals

from olefile import isOleFile

from ingestors.base import Ingestor
from ingestors.support.email import EmailSupport
from ingestors.support.ole import OLESupport
from ingestors.email.outlookmsg_lib import Message


class OutlookMsgIngestor(Ingestor, EmailSupport, OLESupport):
    MIME_TYPES = [
        'appliation/msg',
        'appliation/x-msg',
        'message/rfc822'
    ]
    EXTENSIONS = ['msg']
    SCORE = 10

    def ingest(self, file_path):
        with self.create_temp_dir() as temp_dir:
            message = Message(file_path)
            self.extract_headers_metadata(message.header)
            self.extract_olefileio_metadata(message)
            self.extract_plain_text_content(message.body)
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
