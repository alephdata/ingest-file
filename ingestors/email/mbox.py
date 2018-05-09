import email
import mailbox

from ingestors.email.msg import RFC822Ingestor
from ingestors.util import join_path


class MboxFileIngestor(RFC822Ingestor):
    DEFAULT_MIME = 'application/mbox'
    MIME_TYPES = [DEFAULT_MIME]
    EXTENSIONS = [
        'mbox'
    ]
    MAGIC = 'From '
    SCORE = 6

    def ingest(self, file_path):
        mbox = mailbox.mbox(file_path)
        self.result.mime_type = self.DEFAULT_MIME
        self.result.flag(self.result.FLAG_PACKAGE)

        for i, msg in enumerate(mbox, 1):
            msg_path = join_path(self.work_path, '%s.eml' % i)
            with open(msg_path, 'wb') as fh:
                # Work around for https://bugs.python.org/issue27321.
                try:
                    msg_text = email.message.Message.as_string(msg)
                except KeyError:
                    msg_text = email.message.Message.as_bytes(msg).decode(
                        'utf-8', 'replace'
                    )
                fh.write(msg_text.encode('utf-8'))

            child_id = join_path(self.result.id, str(i))
            self.manager.handle_child(self.result,
                                      msg_path,
                                      id=child_id,
                                      mime_type='message/rfc822')

    @classmethod
    def match(cls, file_path, result=None):
        score = super(MboxFileIngestor, cls).match(file_path, result=result)
        if score < 0:
            # this was added because a lot of mbox files are just called
            # 'inbox' or 'new', without a file suffix.
            with open(file_path, 'rb') as fh:
                if fh.read(len(cls.MAGIC)) == cls.MAGIC:
                    mbox = mailbox.mbox(file_path)
                    for msg in mbox:
                        return cls.SCORE
        return score
