import six
import logging
try:
    import cchardet as chardet
except ImportError:
    import chardet
from normality.encoding import guess_file_encoding, normalize_result

from ingestors.exc import ProcessingException

log = logging.getLogger(__name__)


class EncodingSupport(object):
    """Decode the contents of the given file as plain text by guessing its
    encoding."""

    DEFAULT_ENCODING = 'utf-8'

    def detect_stream_encoding(self, fh, default=DEFAULT_ENCODING):
        return guess_file_encoding(fh, default=default)

    def detect_list_encoding(self, items, default=DEFAULT_ENCODING):
        detector = chardet.UniversalDetector()
        for text in items:
            if not isinstance(text, (six.string_types, six.binary_type)):
                continue
            if not isinstance(text, six.binary_type):
                text = text.encode('utf-8')
            detector.feed(text)
            if detector.done:
                break

        detector.close()
        return normalize_result(detector.result, default)

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
