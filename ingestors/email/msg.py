import os
import six
import logging
import rfc822
from time import mktime
from datetime import datetime

from flanker import mime
from flanker.addresslib import address

from ingestors.base import Ingestor
from ingestors.documents.plain import PlainTextIngestor
from ingestors.documents.html import HTMLIngestor
from ingestors.support.temp import TempFileSupport
from ingestors.util import string_value

log = logging.getLogger(__name__)


class RFC822Ingestor(Ingestor, TempFileSupport):
    MIME_TYPES = ['multipart/mixed']
    EXTENSIONS = ['eml', 'rfc822', 'email', 'msg']
    SCORE = 6

    def write_temp(self, body, temp_dir, file_name):
        out_path = os.path.join(temp_dir, file_name)
        with open(out_path, 'wb') as fh:
            if body is not None:
                if isinstance(body, unicode):
                    body = body.encode('utf-8')
                fh.write(body)
        return out_path

    def ingest_attachment(self, part, temp_dir):
        file_name = string_value(part.detected_file_name)
        mime_type = six.text_type(part.detected_content_type)
        out_path = self.write_temp(part.body, temp_dir, file_name)
        self.manager.handle_child(self.result, out_path, mime_type=mime_type,
                                  file_name=file_name)

    def parse_headers(self, msg):
        self.result.title = msg.subject

        if msg.headers.get('Message-Id'):
            self.result.id = unicode(msg.headers.get('Message-Id'))

        if msg.headers.get('From'):
            addr = address.parse(msg.headers.get('From'))
            if addr is not None:
                if addr.display_name:
                    self.result.author = addr.display_name
                    self.result.people.append(addr.display_name)
                self.result.emails.append(addr.address)

        for hdr in ['To', 'CC', 'BCC']:
            if msg.headers.get(hdr):
                for addr in address.parse_list(msg.headers.get(hdr)):
                    if addr.display_name:
                        self.result.people.append(addr.display_name)
                    self.result.emails.append(addr.address)

        date = msg.headers.get('Date')
        date = rfc822.parsedate(date)
        if date is not None:
            self.result.timestamp = datetime.fromtimestamp(mktime(date))

        self.result.headers = dict([(k, unicode(v)) for k, v in
                                    msg.headers.items()])

    def ingest(self, file_path):
        with open(file_path, 'rb') as emlfh:
            self.ingest_message_data(emlfh.read())

    def ingest_message_data(self, data):
        msg = mime.from_string(data)
        bodies = {'text/plain': msg.body}
        self.parse_headers(msg)
        with self.create_temp_dir() as temp_dir:
            for part in msg.walk():
                if part.is_body():
                    content_type = six.text_type(part.content_type)
                    bodies[content_type] = part.body
                else:
                    self.ingest_attachment(part, temp_dir)

            if 'text/html' in bodies:
                out_path = self.write_temp(bodies['text/html'], temp_dir,
                                           'body.htm')
                self.manager.delegate(HTMLIngestor, self.result, out_path)
            else:
                out_path = self.write_temp(bodies['text/plain'], temp_dir,
                                           'body.txt')
                self.manager.delegate(PlainTextIngestor, self.result, out_path)
