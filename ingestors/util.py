import os
import six
import shutil

from banal import decode_path
from normality import stringify, slugify
from normality import safe_filename as make_filename  # noqa
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


def normalize_extension(extension):
    extension = decode_path(extension)
    if extension is not None:
        if extension.startswith('.'):
            extension = extension[1:]
        if '.' in extension:
            _, extension = os.path.splitext(extension)
        extension = slugify(extension, sep='')
        if extension is not None and len(extension):
            return extension


def string_value(value, encoding=None):
    value = stringify(value, encoding=encoding, encoding_default='utf-8')
    if value is None:
        return
    if isinstance(value, six.text_type):
        value = remove_control_chars(value)
    return value


def join_path(*args):
    args = [decode_path(part) for part in args if part is not None]
    return os.path.join(*args)


def is_file(file_path):
    """Check if a thing is a file, with null guard."""
    file_path = decode_path(file_path)
    if file_path is None:
        return False
    return os.path.isfile(file_path)


def make_directory(file_path):
    """Create a directory, be quiet if it already exists."""
    try:
        os.makedirs(file_path)
    except Exception:
        pass


def remove_directory(file_path):
    """Delete a directory, ignore errors."""
    try:
        shutil.rmtree(file_path, True)
    except Exception:
        pass
