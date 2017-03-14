from chardet.universaldetector import UniversalDetector


class EncodingSupport(object):
    """Provides support for encoding detection."""

    def detect_encoding(self, fio):
        """Returns the encoding of an IO object content.

        :param :py:class:`io.FileIO` fio: The file IO to run detection.
        :rtype: str
        """
        detector = UniversalDetector()

        for line in fio.readlines():
            detector.feed(line)

            if detector.done:
                break

        fio.seek(0)
        detector.close()

        return detector.result['encoding']
