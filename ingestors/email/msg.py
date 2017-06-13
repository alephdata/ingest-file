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
from ingestors.util import join_path, make_filename

log = logging.getLogger(__name__)


class RFC822Ingestor(Ingestor, TempFileSupport):
    MIME_TYPES = ['multipart/mixed']
    EXTENSIONS = ['eml', 'rfc822', 'email', 'msg']
    SCORE = 6

    def write_temp(self, part, temp_dir, file_name):
        file_name = make_filename(file_name, default='attachment')
        out_path = join_path(temp_dir, file_name)
        with open(out_path, 'wb') as fh:
            if part.body is not None:
                body = part.body
                if isinstance(body, six.text_type):
                    body = body.encode('utf-8')
                fh.write(body)
        return out_path

    def ingest_attachment(self, part, temp_dir):
        file_name = part.detected_file_name
        mime_type = six.text_type(part.detected_content_type)
        out_path = self.write_temp(part, temp_dir, file_name)
        child_id = join_path(self.result.id, file_name)
        self.manager.handle_child(self.result, out_path,
                                  id=child_id,
                                  title=file_name,
                                  file_name=file_name,
                                  mime_type=mime_type)

    def parse_headers(self, msg):
        self.result.title = msg.subject

        if msg.message_id:
            self.result.id = six.text_type(msg.message_id)

        if msg.headers.get('From'):
            addr = address.parse(msg.headers.get('From'))
            if addr is not None:
                if addr.display_name and addr.display_name != addr.address:
                    self.result.author = addr.display_name
                    self.result.entities.append(addr.display_name)
                self.result.emails.append(addr.address)

        for hdr in ['To', 'CC', 'BCC']:
            if msg.headers.get(hdr):
                for addr in address.parse_list(msg.headers.get(hdr)):
                    if addr.display_name and addr.display_name != addr.address:
                        self.result.entities.append(addr.display_name)
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
        bodies = {'text/plain': msg}
        self.parse_headers(msg)
        with self.create_temp_dir() as temp_dir:
            for part in msg.walk():
                if part.body is None:
                    continue
                if part.is_body():
                    content_type = unicode(part.content_type)
                    bodies[content_type] = part
                else:
                    self.ingest_attachment(part, temp_dir)

            if 'text/html' in bodies:
                out_path = self.write_temp(bodies['text/html'], temp_dir, 'body.htm')  # noqa
                self.manager.delegate(HTMLIngestor, self.result, out_path)
            else:
                out_path = self.write_temp(bodies['text/plain'], temp_dir, 'body.txt')  # noqa
                self.manager.delegate(PlainTextIngestor, self.result, out_path)
