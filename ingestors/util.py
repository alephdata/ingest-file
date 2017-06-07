from normality import stringify
from normality.cleaning import remove_control_chars


def normalize_mime_type(mime_type):
    """Clean up the mime type a bit."""
    mime_type = stringify(mime_type)
    if mime_type is None:
        return None
    mime_type = mime_type.lower()
    if mime_type in ['application/octet-stream']:
        return None
    return mime_type


def string_value(value, encoding=None):
    value = stringify(value, encoding=encoding, encoding_default='utf-8')
    value = remove_control_chars(value)
    return value
