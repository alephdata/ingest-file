from __future__ import unicode_literals

import six
import logging
from collections import defaultdict
from flanker import mime
from flanker.mime.message.errors import DecodingError
from normality.encoding import normalize_encoding

from ingestors.base import Ingestor
from ingestors.support.email import EmailSupport
from ingestors.exc import ProcessingException

log = logging.getLogger(__name__)


class RFC822Ingestor(Ingestor, EmailSupport):
    MIME_TYPES = [
        'multipart/mixed',
        'message/rfc822'
    ]
    EXTENSIONS = [
        'eml',
        'rfc822',
        'email',
        'msg'
    ]
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
            self.update('message_id', six.text_type(msg.message_id))

        if msg.headers is not None:
            self.extract_headers_metadata(msg.headers.items())

        self.extract_plain_text_content(None)
        self.result.flag(self.result.FLAG_EMAIL)
        bodies = defaultdict(list)

        for part in msg.walk(with_self=True):
            try:
                if part.body is None:
                    continue
            except DecodingError as de:
                log.warning("Cannot decode part [%s]: %s", self.result, de)
                continue

            file_name = part.detected_file_name

            # HACK HACK HACK - WTF flanker?
            # Disposition headers can have multiple filename declarations,
            # flanker decides to concatenate.
            if file_name is not None and len(file_name) > 4:
                half = len(file_name)/2
                if file_name[:half] == file_name[half:]:
                    file_name = file_name[:half]

            mime_type = six.text_type(part.detected_content_type)
            mime_type = normalize_encoding(mime_type, 'text/plain')

            if part.is_attachment():
                self.ingest_attachment(file_name,
                                       mime_type,
                                       part.body,
                                       temp_dir)

            if part.is_body():
                bodies[mime_type].append(part.body)

        if 'text/html' in bodies:
            self.extract_html_content('\n\n'.join(bodies['text/html']))
            self.result.flag(self.result.FLAG_HTML)

        if 'text/plain' in bodies:
            self.extract_plain_text_content('\n\n'.join(bodies['text/plain']))
            self.result.flag(self.result.FLAG_PLAINTEXT)
