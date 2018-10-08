import logging
from collections import defaultdict
from flanker import mime
from flanker.mime.message.errors import DecodingError
from celestial import normalize_mimetype

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
        with open(file_path, 'rb') as fh:
            self.ingest_message(fh.read())

    def ingest_message(self, data):
        try:
            msg = mime.from_string(data)
            if msg.headers is not None:
                self.extract_headers_metadata(msg.headers.items())
        except DecodingError as derr:
            raise ProcessingException('Cannot parse email: %s' % derr)

        try:
            if msg.subject:
                self.update('title', str(msg.subject))
        except DecodingError as derr:
            log.warning("Decoding subject: %s", derr)

        try:
            if msg.message_id:
                self.update('message_id', str(msg.message_id))
        except DecodingError as derr:
            log.warning("Decoding message ID: %s", derr)

        self.extract_plain_text_content(None)
        self.result.flag(self.result.FLAG_EMAIL)
        bodies = defaultdict(list)

        for part in msg.walk(with_self=True):
            try:
                if part.body is None:
                    continue
            except (DecodingError, ValueError) as de:
                log.warning("Cannot decode part [%s]: %s", self.result, de)
                continue

            file_name = part.detected_file_name

            # HACK HACK HACK - WTF flanker?
            # Disposition headers can have multiple filename declarations,
            # flanker decides to concatenate.
            if file_name is not None and len(file_name) > 4:
                half = len(file_name)//2
                if file_name[:half] == file_name[half:]:
                    file_name = file_name[:half]

            mime_type = str(part.detected_content_type)
            mime_type = normalize_mimetype(mime_type)

            if part.is_attachment():
                self.ingest_attachment(file_name,
                                       mime_type,
                                       part.body)

            if part.is_body():
                bodies[mime_type].append(part.body)

        if 'text/html' in bodies:
            self.extract_html_content('\n\n'.join(bodies['text/html']))
            self.result.flag(self.result.FLAG_HTML)

        if 'text/plain' in bodies:
            self.extract_plain_text_content('\n\n'.join(bodies['text/plain']))
            self.result.flag(self.result.FLAG_PLAINTEXT)
