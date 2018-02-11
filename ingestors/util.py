import os
import six
import shutil

from banal import decode_path
from normality import stringify, slugify
from normality import safe_filename as make_filename  # noqa


def safe_string(data, encoding_default='utf-8', encoding=None):
    """Stringify and round-trip through encoding."""
    data = stringify(data,
                     encoding_default=encoding_default,
                     encoding=encoding)
    if isinstance(data, six.text_type):
        data = data.encode(encoding_default, 'replace')
        data = data.decode(encoding_default)
    return data


def safe_dict(data):
    """Clean a dictionary to make sure it contains only valid,
    non-null keys and values."""
    if data is None:
        return

    safe = {}
    for key, value in data.items():
        key = safe_string(key)
        value = safe_string(value)
        if key is not None and value is not None:
            safe[key] = value

    if len(safe):
        return safe


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


def join_path(*args):
    args = [decode_path(part) for part in args if part is not None]
    return os.path.join(*args)


def is_file(file_path):
    """Check if a thing is a file, with null guard."""
    file_path = decode_path(file_path)
    if file_path is None:
        return False
    return os.path.isfile(file_path)


def make_directory(*parts):
    """Create a directory, be quiet if it already exists."""
    file_path = join_path(*parts)
    try:
        os.makedirs(file_path)
    except Exception:
        pass
    return decode_path(file_path)


def remove_directory(file_path):
    """Delete a directory, ignore errors."""
    try:
        shutil.rmtree(file_path, True)
    except Exception:
        pass
