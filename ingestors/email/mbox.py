import os
import logging
import mailbox

from ingestors.email.msg import RFC822Ingestor
from ingestors.support.temp import TempFileSupport

log = logging.getLogger(__name__)


class MboxFileIngestor(RFC822Ingestor, TempFileSupport):
    MIME_TYPES = ['application/mbox']
    EXTENSIONS = ['mbox']
    SCORE = 6

    def ingest(self, file_path):
        mbox = mailbox.mbox(file_path)
        for i, msg in enumerate(mbox):
            with self.create_temp_dir() as temp_dir:
                msg_path = os.path.join(temp_dir, '%s.rfc822' % i)
                with open(msg_path, 'wb') as fh:
                    fh.write(str(msg))
                self.manager.handle_child(self.result, msg_path)
