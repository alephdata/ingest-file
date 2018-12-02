import logging
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
            if not isinstance(text, bytes):
                continue
            detector.feed(text)
            if detector.done:
                break

        detector.close()
        return normalize_result(detector.result, default)

    def read_file_decoded(self, entity, file_path):
        with open(file_path, 'rb') as fh:
            body = fh.read()
            if not entity.has('encoding'):
                result = chardet.detect(body)
                encoding = normalize_result(result, self.DEFAULT_ENCODING)
                entity.set('encoding', encoding)

        for encoding in entity.get('encoding'):
            try:
                body = body.decode(encoding)
                if encoding != self.DEFAULT_ENCODING:
                    log.info("Decoding [%r] as: %s", entity, encoding)
                return body
            except UnicodeDecodeError as ude:
                raise ProcessingException('Error decoding file as %s: %s' %
                                          (encoding, ude))
