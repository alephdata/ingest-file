import os
import six
import sys

from normality import stringify, slugify
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
    if value is None:
        return
    if isinstance(value, six.text_type):
        value = remove_control_chars(value)
    return value


def decode_path(file_path):
    if file_path is None:
        return
    if isinstance(file_path, six.binary_type):
        file_path = file_path.decode(sys.getfilesystemencoding())
    return file_path


def join_path(*args):
    args = [decode_path(part) for part in args if part is not None]
    return os.path.join(*args)


def make_filename(file_name, sep='_', default=None, extension=None):
    if file_name is None:
        return default

    file_name = decode_path(file_name)
    file_name = os.path.basename(file_name)
    file_name, _extension = os.path.splitext(file_name)
    file_name = slugify(file_name, sep=sep)[:200]
    extension = slugify(extension or _extension, sep=sep)
    if extension and len(extension.strip('.')):
        file_name = '.'.join((file_name, extension))

    if not len(file_name.strip()):
        return default
    return decode_path(file_name)
