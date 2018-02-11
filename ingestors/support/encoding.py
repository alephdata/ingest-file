import logging
from normality import guess_file_encoding

from ingestors.exc import ProcessingException

log = logging.getLogger(__name__)


class EncodingSupport(object):
    """Decode the contents of the given file as plain text by guessing its
    encoding."""

    DEFAULT_ENCODING = 'utf-8'

    def detect_stream_encoding(self, fh):
        return guess_file_encoding(fh, default=self.DEFAULT_ENCODING)

    def read_file_decoded(self, file_path):
        encoding = self.result.encoding
        with open(file_path, 'rb') as fh:
            if encoding is None:
                encoding = self.detect_stream_encoding(fh)
            body = fh.read()

        try:
            body = body.decode(encoding)
            if encoding != self.DEFAULT_ENCODING:
                log.info("Decoding [%s] as: %s", self.result, encoding)
            # self.result.encoding = encoding
            return body
        except UnicodeDecodeError as ude:
            raise ProcessingException('Error decoding file  as %s: %s' %
                                      (encoding, ude))
