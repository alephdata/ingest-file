import logging
import mailbox

from ingestors.email.msg import RFC822Ingestor
from ingestors.util import join_path

log = logging.getLogger(__name__)


class MboxFileIngestor(RFC822Ingestor):
    DEFAULT_MIME = 'application/mbox'
    MIME_TYPES = [DEFAULT_MIME]
    EXTENSIONS = ['mbox']
    MAGIC = 'From '
    SCORE = 6

    def ingest(self, file_path, entity):
        mbox = mailbox.mbox(file_path)
        self.result.mime_type = self.DEFAULT_MIME
        self.result.flag(self.result.FLAG_PACKAGE)

        for i, msg in enumerate(mbox.itervalues(), 1):
            # Is there a risk of https://bugs.python.org/issue27321 ?
            msg_path = join_path(self.work_path, '%s.eml' % i)
            try:
                with open(msg_path, 'wb') as fh:
                    fh.write(msg.as_bytes())
            except Exception:
                log.exception("[%s] Cannot extract message %s",
                              self.result, i)
                continue

            child_id = join_path(self.result.id, str(i))
            self.manager.handle_child(self.result,
                                      msg_path,
                                      id=child_id,
                                      mime_type='message/rfc822')

    @classmethod
    def match(cls, file_path, entity):
        score = super(MboxFileIngestor, cls).match(file_path, entity)
        if score < 0:
            # this was added because a lot of mbox files are just called
            # 'inbox' or 'new', without a file suffix.
            with open(file_path, 'rb') as fh:
                if fh.read(len(cls.MAGIC)) == cls.MAGIC:
                    mbox = mailbox.mbox(file_path)
                    for msg in mbox:
                        return cls.SCORE
        return score
