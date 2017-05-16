import io
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
    with io.open(file_path, 'rb') as fio:
        ingestor, data, detached_data = ingest(fio, file_path)

        if detached_data:
            data['pages'] = detached_data

        if not echo:
            return data

        print(json.dumps(data, sort_keys=True, indent=2, default=json_default))
