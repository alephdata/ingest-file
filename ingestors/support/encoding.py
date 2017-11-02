import logging

from normality import guess_file_encoding
from normality.cleaning import remove_control_chars

from ingestors.exc import ProcessingException

log = logging.getLogger(__name__)


class EncodingSupport(object):
    """Decode the contents of the given file as plain text by guessing its
    encoding."""

    DEFAULT_ENCODING = 'utf-8'

    def detect_stream_encoding(self, fh):
        return guess_file_encoding(fh, self.DEFAULT_ENCODING)

    def read_file_decoded(self, file_path):
        with open(file_path, 'rb') as fh:
            encoding = self.detect_stream_encoding(fh)
            body = fh.read()

        if encoding != self.DEFAULT_ENCODING:
            log.info("Decoding %s as: %s", self.result.label, encoding)
        try:
            body = body.decode(encoding, 'replace')
            body = remove_control_chars(body)
            if not self.result.encoding:
                self.result.encoding = encoding
            return body
        except UnicodeDecodeError as ude:
            raise ProcessingException('Error decoding file [%s]: %s' %
                                      (encoding, ude))
