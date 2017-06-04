import json
import decimal
import datetime

from ingestors import ingest


def json_default(obj):
    """Simple helper to provide JSON support for dates and decimals."""
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()

    if isinstance(obj, decimal.Decimal):
        return float(obj)


def cli(file_path, echo=True):
    """CLI main method."""
    result = ingest(file_path)

    if not echo:
        return result

    print(json.dumps(result.to_dict(), sort_keys=True, indent=2,
                     default=json_default))
