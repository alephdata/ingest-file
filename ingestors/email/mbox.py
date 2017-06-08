import six
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
            for i, msg in enumerate(mbox):
                msg_path = make_filename(six.text_type(i), extension='eml')
                msg_path = join_path(temp_dir, msg_path)
                with open(msg_path, 'wb') as fh:
                    fh.write(str(msg))
                self.manager.handle_child(self.result, msg_path)
