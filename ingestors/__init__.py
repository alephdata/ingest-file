"""Provides a set of ingestors based on different file types."""
import logging

from ingestors.base import IngestorManager

__version__ = '0.3.0'

logging.getLogger('chardet').setLevel(logging.INFO)


def ingest(file_path):
    """Simple wrapper to run ingestors on a file.

    :param file_path: The file path.
    :type file_path: str
    :return: Tuple, the ingestor object, its data and detached ingestors data.
    :rtype: tuple
    """
    manager = IngestorManager({})
    return manager.execute(file_path)

    # ingestor_class, mime_type = TextIngestor.match(fio)
    #
    # if not ingestor_class:
    #     return None, None, None
    #
    # ingestor = ingestor_class(fio, file_path, mime_type=mime_type)
    # ingestor.run()
    # detached_data = map(lambda c: c.result, getattr(ingestor, 'detached', []))
    #
    # return ingestor, ingestor.result, detached_data
