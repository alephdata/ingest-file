from ingestors.log import get_logger
from msglite import Message
from olefile import isOleFile
from normality import stringify
from followthemoney import model
from email.utils import parsedate_to_datetime

from ingestors.ingestor import Ingestor
from ingestors.support.email import EmailSupport, EmailIdentity
from ingestors.support.temp import TempFileSupport
from ingestors.support.ole import OLESupport
from ingestors.exc import ProcessingException

log = get_logger(__name__)
RTF_MIME = "application/rtf"


class OutlookMsgIngestor(Ingestor, EmailSupport, OLESupport, TempFileSupport):
    MIME_TYPES = [
        "application/msg",
        "application/x-msg",
        "application/vnd.ms-outlook",
        "msg/rfc822",
    ]
    EXTENSIONS = ["msg"]
    SCORE = 10

    def get_identity(self, name, email):
        return EmailIdentity(self.manager, name, email)

    def ingest(self, file_path, entity):
        entity.schema = model.get("Email")
        try:
            msg = Message(file_path.as_posix())
        except Exception as exc:
            msg = "Cannot open message file: %s" % exc
            raise ProcessingException(msg) from exc

        self.extract_olefileio_metadata(msg.ole, entity)
        self.ingest_message(msg, entity)

    def ingest_message(self, msg, entity):
        try:
            self.extract_msg_headers(entity, msg.header)
        except Exception:
            log.exception("Cannot parse Outlook-stored headers")

        entity.add("subject", msg.subject)
        entity.add("threadTopic", msg.getStringField("0070"))
        entity.add("encoding", msg.encoding)
        entity.add("bodyText", msg.body)
        entity.add("bodyHtml", msg.htmlBody)
        entity.add("messageId", self.parse_message_ids(msg.message_id))

        try:
            rtf_body = msg.rtfBody
        except Exception:
            log.exception("Cannot parse RTF body of the email")
            rtf_body = None

        if rtf_body is not None:
            rtf_path = self.make_work_file("body.rtf")
            with open(rtf_path, "wb") as fh:
                fh.write(rtf_body)
            checksum = self.manager.store(rtf_path, mime_type=RTF_MIME)
            rtf_path.unlink()

            child = self.manager.make_entity("Document", parent=entity)
            child.make_id(entity.id, "outlook-msg.rtf.body")
            child.add("fileName", "body.rtf")
            child.add("contentHash", checksum)
            child.add("mimeType", RTF_MIME)
            self.manager.queue_entity(child)

        if not entity.has("inReplyTo"):
            entity.add("inReplyTo", self.parse_references(msg.references, []))

        try:
            date = parsedate_to_datetime(msg.date).isoformat()
            entity.add("date", date)
        except Exception:
            log.warning("Could not parse date: %s", msg.date)

        # sender name and email
        sender = self.get_identities(msg.sender)
        self.apply_identities(entity, sender, "emitters", "sender")

        # received by
        sender = self.get_identity(
            msg.getStringField("0040"), msg.getStringField("0076")
        )
        self.apply_identities(entity, sender, "emitters")

        froms = self.get_identities(msg.getStringField("1046"))
        self.apply_identities(entity, froms, "emitters", "from")

        tos = self.get_identities(msg.to)
        self.apply_identities(entity, tos, "recipients", "to")

        ccs = self.get_identities(msg.cc)
        self.apply_identities(entity, ccs, "recipients", "cc")

        bccs = self.get_identities(msg.bcc)
        self.apply_identities(entity, bccs, "recipients", "bcc")

        self.resolve_message_ids(entity)
        for attachment in msg.attachments:
            if attachment.type == "msg":
                child = self.manager.make_entity("Email", parent=entity)
                child.make_id(entity.id, attachment.data.prefix)
                child.add("fileName", attachment.long_filename)
                child.add("fileName", attachment.short_filename)
                child.add("mimeType", "application/vnd.ms-outlook")
                self.ingest_message(attachment.data, child)
                self.manager.emit_entity(child, fragment=attachment.data.prefix)
            if attachment.type == "data":
                name = stringify(attachment.long_filename)
                name = name or stringify(attachment.short_filename)
                self.ingest_attachment(
                    entity, name, attachment.content_type, attachment.data
                )

    @classmethod
    def match(cls, file_path, entity):
        score = super(OutlookMsgIngestor, cls).match(file_path, entity)
        if score > 0 and not isOleFile(file_path):
            return -1
        return score
