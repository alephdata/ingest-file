import logging

from ingestors.base import Ingestor

log = logging.getLogger(__name__)


class IgnoreIngestor(Ingestor):
    MIME_TYPES = [
        'application/x-pkcs7-mime',
        'application/pkcs7-mime',
        'application/pkcs7-signature',
        'application/x-pkcs7-signature',
        'application/x-pkcs12'
        'application/pgp-encrypted',
        'application/x-shockwave-flash',
        'application/vnd.apple.pkpass',
        'application/x-executable',
        'application/x-mach-binary',
        'application/x-sharedlib',
        'application/x-dosexec',
        'application/x-java-keystore',
        'application/java-archive',
        'application/font-sfnt',
        'application/vnd.ms-office.vbaproject',
        'application/x-x509-ca-cert',
        'text/calendar',
        'text/css',
        'application/vnd.ms-opentype',
        'application/x-font-ttf',
    ]
    EXTENSIONS = [
        'json',
        'exe',
        'dll',
        'ini',
        'class',
        'jar',
        'psd',  # adobe photoshop
        'indd',  # adobe indesign
        'sql',
        'dat',
        'log',
        'pbl',
        'p7m',
        'plist',
        'ics',
        'axd'
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
        if result.size is not None and result.size == 0:
            return cls.SCORE * 100
        if result.file_name in cls.NAMES:
            return cls.SCORE
        return super(IgnoreIngestor, cls).match(file_path, result=result)
