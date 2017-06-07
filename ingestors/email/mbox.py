import logging
import mailbox

from ingestors.email.msg import RFC822Ingestor

log = logging.getLogger(__name__)


class MboxFileIngestor(RFC822Ingestor):
    MIME_TYPES = ['application/mbox']
    EXTENSIONS = ['mbox']
    SCORE = 6

    def ingest(self, meta, local_path):
        mbox = mailbox.mbox(local_path)
        for msg in mbox:
            try:
                self.ingest_message_data(meta.clone(),
                                         msg.as_string())
            except Exception as ex:
                log.exception(ex)
