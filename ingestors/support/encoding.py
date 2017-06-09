import logging

from chardet.universaldetector import UniversalDetector
from normality import guess_encoding, stringify
from normality.cleaning import remove_control_chars

from ingestors.exc import ProcessingException

log = logging.getLogger(__name__)


class EncodingSupport(object):
    """Decode the contents of the given file as plain text by guessing its
    encoding."""

    DEFAULT_ENCODING = 'utf-8'

    def _normalize_encoding(self, encoding):
        if encoding is None:
            return self.DEFAULT_ENCODING
        encoding = encoding.lower().strip()
        if encoding in ['', 'ascii']:
            return self.DEFAULT_ENCODING
        return encoding

    def detect_stream_encoding(self, fh):
        detector = UniversalDetector()
        while True:
            block = fh.read(4096)
            if not block:
                break
            detector.feed(block)
            if detector.done:
                break

        detector.close()
        encoding = detector.result.get('encoding')
        return self._normalize_encoding(encoding)

    def read_file_decoded(self, file_path):
        with open(file_path, 'rb') as fh:
            body = fh.read()

        default_encoding = self.result.encoding or 'utf-8'
        encoding = guess_encoding(body, default_encoding)
        encoding = self._normalize_encoding(encoding)
        if encoding != self.DEFAULT_ENCODING:
            log.info("Decoding %s as: %s", self.result.label, encoding)
        try:
            body = stringify(body, encoding=encoding)
            body = remove_control_chars(body)
            if not self.result.encoding:
                self.result.encoding = encoding
            return body
        except UnicodeDecodeError as ude:
            raise ProcessingException('Error decoding file [%s]: %s' %
                                      (encoding, ude))
