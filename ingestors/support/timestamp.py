from ingestors.log import get_logger
from banal import ensure_list
from normality import stringify
from datetime import datetime, date

log = get_logger(__name__)


class TimestampSupport(object):
    """Provides helpers for date and time parsing."""

    TIMESTAMP_FORMATS = (
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y:%m:%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y:%m:%d %H:%M:%SZ",  # exif
        "%Z %Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%Y%m%d",
    )

    def parse_timestamp(self, raw, fmt=None):
        if isinstance(raw, (datetime, date)):
            return raw
        text = stringify(raw)
        if text is None:
            return
        formats = ensure_list(fmt) or self.TIMESTAMP_FORMATS
        for fmt in formats:
            try:
                if "." in text and "." not in fmt:
                    text, _ = text.split(".", 1)
                return datetime.strptime(text, fmt)
            except Exception:
                pass
        log.warning("Could not parse timestamp: %r", raw)
        return raw
