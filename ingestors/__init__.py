"""Provides a set of ingestors based on different file types."""
import logging

from ingestors.doc import DocumentIngestor  # noqa
from ingestors.html import HTMLIngestor  # noqa
from ingestors.image import ImageIngestor  # noqa
from ingestors.pdf import PDFIngestor  # noqa
from ingestors.tabular import TabularIngestor  # noqa
from ingestors.text import TextIngestor  # noqa

__version__ = '0.2.0'

logging.getLogger('chardet').setLevel(logging.INFO)


def ingest(fio, file_path):
    """Simple wrapper to run ingestors on a file.

    :param fio: An instance of the file to process.
    :type fio: py:class:`io.FileIO`
    :param file_path: The file path.
    :type file_path: str
    :return: Tuple, the ingestor object, its data and detached ingestors data.
    :rtype: tuple
    """
    ingestor_class, mime_type = TextIngestor.match(fio)

    if not ingestor_class:
        return None, None, None

    ingestor = ingestor_class(fio, file_path, mime_type=mime_type)
    ingestor.run()
    detached_data = map(lambda c: c.result, getattr(ingestor, 'detached', []))

    return ingestor, ingestor.result, detached_data
