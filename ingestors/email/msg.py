from __future__ import unicode_literals

import six
import logging
from collections import defaultdict
from normality import safe_filename
from flanker import mime
from flanker.mime.message.errors import DecodingError

from ingestors.base import Ingestor
from ingestors.support.email import EmailSupport
from ingestors.exc import ProcessingException
from ingestors.util import join_path

log = logging.getLogger(__name__)


class RFC822Ingestor(Ingestor, EmailSupport):
    MIME_TYPES = [
        'multipart/mixed',
        'message/rfc822'
    ]
    EXTENSIONS = ['eml', 'rfc822', 'email', 'msg']
    SCORE = 6

    def ingest(self, file_path):
        with self.create_temp_dir() as temp_dir:
            with open(file_path, 'rb') as fh:
                self.ingest_message(fh.read(), temp_dir)

    def ingest_message(self, data, temp_dir):
        try:
            msg = mime.from_string(data)
        except DecodingError as derr:
            raise ProcessingException('Cannot parse email: %s' % derr)

        self.update('title', msg.clean_subject)
        if msg.message_id:
            self.update('id', msg.message_id)

        self.extract_headers_metadata(msg.headers)
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
                self.ingest_attachment(file_name,
                                       mime_type,
                                       part.body,
                                       temp_dir)

            if part.is_body():
                bodies[mime_type].append(part.body)

        if 'text/html' in bodies:
            self.extract_html_content('\n\n'.join(bodies['text/html']))

        if 'text/plain' in bodies:
            self.extract_plain_text_content('\n\n'.join(bodies['text/plain']))
