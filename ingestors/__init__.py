"""Provides a set of ingestors based on different file types."""

import logging

__version__ = "4.0.3-rc4"

logging.getLogger("chardet").setLevel(logging.INFO)
logging.getLogger("PIL").setLevel(logging.INFO)
logging.getLogger("google.auth").setLevel(logging.INFO)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("msglite").setLevel(logging.WARNING)
logging.getLogger("pika").setLevel(logging.WARNING)
