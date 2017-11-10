from __future__ import unicode_literals

import six
import rfc822
import logging
from time import mktime
from datetime import datetime
from collections import defaultdict
from normality import safe_filename
from flanker import mime
from flanker.addresslib import address
from flanker.mime.message.errors import DecodingError

from ingestors.base import Ingestor
from ingestors.support.temp import TempFileSupport
from ingestors.support.plain import PlainTextSupport
from ingestors.support.html import HTMLSupport
from ingestors.exc import ProcessingException
from ingestors.util import join_path

log = logging.getLogger(__name__)


class RFC822Ingestor(Ingestor, TempFileSupport, HTMLSupport, PlainTextSupport):
    MIME_TYPES = ['multipart/mixed']
    EXTENSIONS = ['eml', 'rfc822', 'email', 'msg']
    SCORE = 6

    def write_temp(self, part, temp_dir, file_name):
        file_name = safe_filename(file_name, default='attachment')
        out_path = join_path(temp_dir, file_name)
        with open(out_path, 'wb') as fh:
            if part.body is not None:
                body = part.body
                if isinstance(body, six.text_type):
                    body = body.encode('utf-8')
                fh.write(body)
        return out_path

    def parse_headers(self, msg):
        self.result.title = msg.subject

        if msg.message_id and self.result.id is None:
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
        with self.create_temp_dir() as temp_dir:
            with open(file_path, 'rb') as fh:
                self.ingest_message(fh.read(), temp_dir)

    def ingest_message(self, data, temp_dir):
        try:
            msg = mime.from_string(data)
        except DecodingError as derr:
            raise ProcessingException('Cannot parse email: %s' % derr)
        self.parse_headers(msg)
        self.extract_plain_text_content(None)
        bodies = defaultdict(list)
        for part in msg.walk(with_self=True):
            try:
                if part.body is None:
                    continue
            except DecodingError:
                log.error("Cannot decode part: [%s]", self.result)
                continue

            file_name = part.detected_file_name
            mime_type = six.text_type(part.detected_content_type)
            mime_type = mime_type.lower().strip()

            if part.is_attachment():
                out_path = self.write_temp(part, temp_dir, file_name)
                child_id = join_path(self.result.id, file_name)
                self.manager.handle_child(self.result, out_path,
                                          id=child_id,
                                          file_name=file_name,
                                          mime_type=mime_type)

            if part.is_body():
                bodies[mime_type].append(part.body)

        if 'text/html' in bodies:
            self.extract_html_content('\n\n'.join(bodies['text/html']))

        if 'text/plain' in bodies:
            self.extract_plain_text_content('\n\n'.join(bodies['text/plain']))
