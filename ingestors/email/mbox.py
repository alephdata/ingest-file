import logging
import mailbox

from ingestors.email.msg import RFC822Ingestor
from ingestors.support.temp import TempFileSupport
from ingestors.util import join_path, make_filename

log = logging.getLogger(__name__)


class MboxFileIngestor(RFC822Ingestor, TempFileSupport):
    MIME_TYPES = ['application/mbox']
    EXTENSIONS = ['mbox']
    SCORE = 6

    def ingest(self, file_path):
        mbox = mailbox.mbox(file_path)
        with self.create_temp_dir() as temp_dir:
            for i, msg in enumerate(mbox, 1):
                msg_name = 'message%s' % i
                msg_name = make_filename(msg_name, extension='eml')
                msg_path = join_path(temp_dir, msg_name)
                with open(msg_path, 'wb') as fh:
                    fh.write(str(msg))
                child_id = join_path(self.result.id, msg_name)
                self.manager.handle_child(self.result, msg_path,
                                          id=child_id,
                                          mime_type='multipart/mixed')
