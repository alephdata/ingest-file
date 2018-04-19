import os

from ingestors.base import Ingestor
from ingestors.support.encoding import EncodingSupport
from ingestors.support.plain import PlainTextSupport
from ingestors.exc import ProcessingException


class PlainTextIngestor(Ingestor, EncodingSupport, PlainTextSupport):
    """Plan text file ingestor class.

    Extracts the text from the document and enforces unicode on it.
    """
    MIME_TYPES = [
        'text/plain',
        'text/x-c',
        'text/x-c++',
        'text/x-diff',
        'text/x-python',
        'text/x-shellscript',
        'text/x-java',
        'text/x-php',
        'text/troff',
        'text/x-ruby',
        'text/x-pascal',
        'text/x-msdos-batch',
        'text/x-yaml',
        'text/x-makefile',
        'text/x-perl',  # %^&%*^&%*%^
        'text/x-objective-c',
        'text/x-msdos-batch',
        'text/x-asm',
        'text/x-csrc',
        'text/x-sh',
        'text/javascript',
        'text/x-algol68',
    ]
    MAX_SIZE = 4 * 1024 * 1024
    SCORE = 1

    def ingest(self, file_path):
        """Ingestor implementation."""
        file_size = self.result.size or os.path.getsize(file_path)
        if file_size > self.MAX_SIZE:
            raise ProcessingException("Text file is too large.")

        text = self.read_file_decoded(file_path)
        if text is None:
            raise ProcessingException("Document could not be decoded.")

        self.result.flag(self.result.FLAG_PLAINTEXT)
        self.extract_plain_text_content(text)
