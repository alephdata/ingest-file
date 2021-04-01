import email
import logging
from email.policy import default
from email.errors import MessageError
from followthemoney import model

from ingestors.email.msg import RFC822Ingestor
from ingestors.exc import ProcessingException

log = logging.getLogger(__name__)


class AppleEmlxIngestor(RFC822Ingestor):
    MIME_TYPES = []
    EXTENSIONS = ["emlx"]
    SCORE = 8

    def ingest(self, file_path, entity):
        entity.schema = model.get("Email")
        try:
            with open(file_path, "rb") as fh:
                msg_len = int(fh.readline().strip())
                data = fh.read(msg_len)
                msg = email.message_from_bytes(data, policy=default)
        except (MessageError, ValueError, IndexError) as err:
            raise ProcessingException("Cannot parse email: %s" % err) from err

        self.ingest_msg(entity, msg)
