import re
import email
import logging
from email.header import decode_header, make_header
from email.policy import default
from email.errors import MessageError
from html import escape
from pantomime import normalize_mimetype
from followthemoney import model

from ingestors.ingestor import Ingestor
from ingestors.support.email import EmailSupport
from ingestors.support.encoding import EncodingSupport
from ingestors.exc import ProcessingException

log = logging.getLogger(__name__)

linesep_splitter = re.compile(r'\n|\r')

def my_header_fetch_parse(name, value):
    if hasattr(value, 'name'):
        return value
    v = str(make_header(decode_header(value)))
    v = ''.join(linesep_splitter.split(v))
    return email.policy.default.header_factory(name, v)

class RFC822Ingestor(Ingestor, EmailSupport, EncodingSupport):
    MIME_TYPES = ["multipart/mixed", "message/rfc822"]
    BODY_HTML = "text/html"
    BODY_PLAIN = "text/plain"
    BODY_TYPES = [BODY_HTML, BODY_PLAIN]
    BODY_RFC822 = "message/rfc822"
    DISPLAY_HEADERS = ["from", "to", "cc", "bcc", "subject", "reply-to", "date"]
    EXTENSIONS = ["eml", "rfc822", "email", "msg"]
    SCORE = 7

    def has_alternative(self, parent, content_type):
        if not parent:
            return False

        if normalize_mimetype(parent.get_content_type()) != "multipart/alternative":
            return False

        for part in parent.get_payload():
            if normalize_mimetype(part.get_content_type()) == content_type:
                return True

        return False

    def make_html_alternative(self, text):
        if not text:
            return None

        return escape(text).strip().replace("\n", "<br>")

    def decode_part(self, part):
        charset = part.get_content_charset()
        payload = part.get_payload(decode=True)
        return self.decode_string(payload, charset)

    def parse_html_part(self, entity, part, parent):
        payload = self.decode_part(part)
        text = self.extract_html_content(
            entity, payload, extract_metadata=False, add_index_text=False
        )

        if not self.has_alternative(parent, "text/plain"):
            entity.add("bodyText", text)

    def parse_plaintext_part(self, entity, part, parent):
        payload = self.decode_part(part)
        entity.add("bodyText", payload)

        if not self.has_alternative(parent, "text/html"):
            html = self.make_html_alternative(payload)
            entity.add("bodyHtml", html)

    def parse_rfc822_part(self, entity, part, parent):
        msg = part.get_payload(0)
        headers = [
            f"{name}: {value}"
            for name, value in msg.items()
            if name.lower() in self.DISPLAY_HEADERS
        ]
        text = "\n".join(headers)
        html = self.make_html_alternative(text)
        entity.add("bodyText", text)
        entity.add("bodyHtml", html)

        self.parse_parts(entity, part)

    def parse_part(self, entity, part, parent):
        mime_type = normalize_mimetype(part.get_content_type())
        file_name = part.get_filename()
        is_body_type = mime_type in self.BODY_TYPES
        is_attachment = part.is_attachment()
        is_attachment = is_attachment or file_name is not None
        is_attachment = is_attachment or (not is_body_type and not part.is_multipart())

        if is_attachment:
            if part.is_multipart():
                # The attachment is an email
                payload = str(part.get_payload(i=0))
            else:
                payload = part.get_payload(decode=True)
            self.ingest_attachment(entity, file_name, mime_type, payload)
            return

        if self.BODY_RFC822 in mime_type:
            self.parse_rfc822_part(entity, part, parent)
            return

        if part.is_multipart():
            self.parse_parts(entity, part)
            return

        if self.BODY_HTML in mime_type:
            self.parse_html_part(entity, part, parent)
            return

        if self.BODY_PLAIN in mime_type:
            self.parse_plaintext_part(entity, part, parent)
            return

        log.error("Dangling MIME fragment: %s", part)

    def parse_parts(self, entity, parent):
        for part in parent.get_payload():
            self.parse_part(entity, part, parent)

    def ingest_msg(self, entity, msg):
        self.extract_msg_headers(entity, msg)
        self.resolve_message_ids(entity)

        if msg.is_multipart():
            self.parse_parts(entity, msg)
        else:
            self.parse_part(entity, msg, None)

    def ingest(self, file_path, entity):
        entity.schema = model.get("Email")
        try:
            with open(file_path, "rb") as fh:
                policy = default.clone(header_fetch_parse=my_header_fetch_parse)
                msg = email.message_from_binary_file(fh, policy=policy)
        except (MessageError, ValueError, IndexError) as err:
            raise ProcessingException("Cannot parse email: %s" % err) from err

        self.ingest_msg(entity, msg)
