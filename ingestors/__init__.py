"""Provides a set of ingestors based on different file types."""
import logging
from ingestors.log import get_logger

__version__ = "3.17.1"

get_logger("chardet").setLevel(logging.INFO)
get_logger("PIL").setLevel(logging.INFO)
get_logger("google.auth").setLevel(logging.INFO)
get_logger("urllib3").setLevel(logging.WARNING)
get_logger("msglite").setLevel(logging.WARNING)
