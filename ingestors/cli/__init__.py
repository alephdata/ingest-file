import decimal
import datetime

from ingestors import ingest


def json_default(obj):
    """Simple helper to provide JSON support for dates and decimals."""
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()

    if isinstance(obj, decimal.Decimal):
        return float(obj)


def cli(file_path):
    """CLI main method."""
    ingest(file_path)
