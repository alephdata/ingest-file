"""Provides a set of ingestors based on different file types."""
import logging

__version__ = '0.13.0'

logging.getLogger('chardet').setLevel(logging.INFO)
logging.getLogger('PIL').setLevel(logging.INFO)
logging.getLogger('google.auth').setLevel(logging.INFO)
