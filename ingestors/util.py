import os
import six
import shutil

from banal import decode_path
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


def make_filename(file_name, sep='_', default=None, extension=None):
    """Create a secure filename for plain file system storage."""
    if file_name is None:
        return decode_path(default)

    file_name = decode_path(file_name)
    file_name = os.path.basename(file_name)
    file_name, _extension = os.path.splitext(file_name)
    file_name = slugify(file_name, sep=sep) or ''
    file_name = file_name[:250]
    extension = slugify(extension or _extension, sep=sep)
    if extension and len(extension.strip('.')) and len(file_name):
        file_name = '.'.join((file_name, extension))

    if not len(file_name.strip()):
        return decode_path(default)
    return decode_path(file_name)


def make_directory(file_path):
    """Create a directory, be quiet if it already exists."""
    try:
        os.makedirs(file_path)
    except:
        pass


def remove_directory(file_path):
    """Delete a directory, ignore errors."""
    try:
        shutil.rmtree(file_path, True)
    except:
        pass
