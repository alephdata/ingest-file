import logging

from ingestors.base import Ingestor

log = logging.getLogger(__name__)


class IgnoreIngestor(Ingestor):
    MIME_TYPES = [
        'application/x-pkcs7-mime',
        'application/pkcs7-mime',
        'application/pkcs7-signature',
        'application/x-pkcs7-signature',
        'application/vnd.apple.pkpass',
        'text/calendar'
    ]
    EXTENSIONS = [
        'json',
        'yml',
        'yaml',
        'exe',
        'dll',
        'ini',
        'class',
        'psd',  # adobe photoshop
        'indd',  # adobe indesign
        'sql',
        'avi',
        'mpg',
        'mpeg',
        'mkv',
        'dat',
        'log',
        'pbl',
        'p7m',
        'plist',
        'ics'
    ]
    NAMES = [
        '.DS_Store',
        'Thumbs.db',
        '.gitignore'
    ]
    SCORE = 2

    def ingest(self, file_path):
        log.info("[%s] will be ignored but stored.", self.result)

    @classmethod
    def match(cls, file_path, result=None):
        if result.file_name in cls.NAMES:
            return cls.SCORE
        return super(IgnoreIngestor, cls).match(file_path, result=result)
