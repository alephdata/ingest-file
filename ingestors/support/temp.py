import contextlib
import tempfile

from ingestors.util import decode_path, remove_directory


class TempFileSupport(object):
    """Provides helpers for file system related tasks."""

    @contextlib.contextmanager
    def create_temp_dir(self, *args, **kwargs):
        """Creates a temporary folder and removes it later."""
        temp_dir = tempfile.mkdtemp(*args, **kwargs)
        try:
            yield decode_path(temp_dir)
        finally:
            remove_directory(temp_dir)
