"""Provides a set of ingestors based on different file types."""

from .doc import DocumentIngestor  # noqa
from .html import HTMLIngestor  # noqa
from .image import ImageIngestor  # noqa
from .pdf import PDFIngestor  # noqa
from .tabular import TabularIngestor  # noqa
from .text import TextIngestor  # noqa

__version__ = '0.1.0'


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
