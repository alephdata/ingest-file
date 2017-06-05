from normality import guess_encoding, stringify
from normality.cleaning import remove_control_chars

from ingestors.exc import ProcessingException


class EncodingSupport(object):
    """Decode the contents of the given file as plain text by guessing its
    encoding."""

    def read_file_decoded(self, file_path):
        with open(file_path, 'rb') as fh:
            body = fh.read()

        default_encoding = self.result.encoding or 'utf-8'
        encoding = guess_encoding(body, default_encoding)
        try:
            body = stringify(body, encoding=encoding)
            body = remove_control_chars(body)
            if not self.result.encoding:
                self.result.encoding = encoding
            return body
        except UnicodeDecodeError as ude:
            raise ProcessingException('Error decoding file [%s]: %s' %
                                      (encoding, ude))
