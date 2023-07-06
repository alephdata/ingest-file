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

    def walk_parts(self, part, parent=None):
        # This is a modified version of the `walk` method from `email.message.Message`.
        # Instead of just the subparts, it yields tuples that also include a reference to
        # the parent part. This is necessary in order to determine whether a part has an
        # alternative HTML or plaintext representation.
        yield (part, parent)
        if part.is_multipart():
            for subpart in part.get_payload():
                yield from self.walk_parts(subpart, part)

    def decode_part(self, part):
        charset = part.get_content_charset()
        payload = part.get_payload(decode=True)
        return self.decode_string(payload, charset)

    def has_alternative(self, parent, content_type):
        if not parent:
            return False

        if normalize_mimetype(parent.get_content_type()) != "multipart/alternative":
            return False

        for part in parent.get_payload():
            if normalize_mimetype(part.get_content_type()) == content_type:
                return True

        return False

    def parse_part(self, entity, part, parent):
        if part.is_multipart():
            return

        mime_type = normalize_mimetype(part.get_content_type())
        file_name = part.get_filename()
        is_attachment = part.is_attachment()
        is_attachment = is_attachment or file_name is not None
        is_attachment = is_attachment or mime_type not in self.BODY_TYPES

        if is_attachment:
            payload = part.get_payload(decode=True)
            self.ingest_attachment(entity, file_name, mime_type, payload)
        elif self.BODY_HTML in mime_type:
            payload = self.decode_part(part)
            text = self.extract_html_content(entity, payload, extract_metadata=False)
            if not self.has_alternative(parent, "text/plain"):
                entity.add("bodyText", text)
        elif self.BODY_PLAIN in mime_type:
            payload = self.decode_part(part)
            entity.add("bodyText", payload)
            if not self.has_alternative(parent, "text/html"):
                html = payload or ""
                html = escape(html).strip().replace("\n", "<br>")
                entity.add("bodyHtml", html)
        else:
            log.error("Dangling MIME fragment: %s", part)

    def ingest_msg(self, entity, msg):
        self.extract_msg_headers(entity, msg)
        self.resolve_message_ids(entity)

        for part, parent in self.walk_parts(msg):
            self.parse_part(entity, part, parent)

    def ingest(self, file_path, entity):
        entity.schema = model.get("Email")
        try:
            with open(file_path, "rb") as fh:
                msg = email.message_from_binary_file(fh, policy=default)
        except (MessageError, ValueError, IndexError) as err:
            raise ProcessingException("Cannot parse email: %s" % err) from err

        self.ingest_msg(entity, msg)
