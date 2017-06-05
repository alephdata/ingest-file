from normality import stringify


def normalize_mime_type(mime_type):
    """Clean up the mime type a bit."""
    mime_type = stringify(mime_type)
    if mime_type is None:
        return None
    mime_type = mime_type.lower()
    if mime_type in ['application/octet-stream']:
        return None
    return mime_type
