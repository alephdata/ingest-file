import email
import logging
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


class RFC822Ingestor(Ingestor, EmailSupport, EncodingSupport):
    MIME_TYPES = ["multipart/mixed", "message/rfc822"]
    BODY_HTML = "text/html"
    BODY_PLAIN = "text/plain"
    BODY_TYPES = [BODY_HTML, BODY_PLAIN]
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

    def decode_part(self, part):
        charset = part.get_content_charset()
        payload = part.get_payload(decode=True)
        return self.decode_string(payload, charset)

    def parse_html_part(self, entity, part, parent):
        payload = self.decode_part(part)
        text = self.extract_html_content(entity, payload, extract_metadata=False)

        if not self.has_alternative(parent, "text/plain"):
            entity.add("bodyText", text)

    def parse_plaintext_part(self, entity, part, parent):
        payload = self.decode_part(part)
        entity.add("bodyText", payload)

        if not self.has_alternative(parent, "text/html"):
            html = payload or ""
            html = escape(html).strip().replace("\n", "<br>")
            entity.add("bodyHtml", html)

    def parse_part(self, entity, part, parent):
        if part.is_multipart():
            self.parse_parts(entity, part)
            return

        mime_type = normalize_mimetype(part.get_content_type())
        file_name = part.get_filename()
        is_attachment = part.is_attachment()
        is_attachment = is_attachment or file_name is not None
        is_attachment = is_attachment or mime_type not in self.BODY_TYPES

        if is_attachment:
            payload = part.get_payload(decode=True)
            self.ingest_attachment(entity, file_name, mime_type, payload)
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
                msg = email.message_from_binary_file(fh, policy=default)
        except (MessageError, ValueError, IndexError) as err:
            raise ProcessingException("Cannot parse email: %s" % err) from err

        self.ingest_msg(entity, msg)
