"""Provides a set of ingestors based on different file types."""
import logging

from ingestors.manager import Manager
from ingestors.result import Result  # noqa

__version__ = '0.3.0'

logging.getLogger('chardet').setLevel(logging.INFO)
logging.getLogger('flanker').setLevel(logging.INFO)
logging.getLogger('PIL').setLevel(logging.INFO)
logging.getLogger('google.auth').setLevel(logging.INFO)


def ingest(file_path):
    """Simple wrapper to run ingestors on a file.

    :param file_path: The file path.
    :type file_path: str
    :return: Tuple, the ingestor object, its data and detached ingestors data.
    :rtype: tuple
    """
    manager = Manager({})
    return manager.ingest(file_path)
