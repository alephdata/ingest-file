import contextlib
import shutil
import tempfile


class TempFileSupport(object):
    """Provides helpers for file system related tasks."""

    @contextlib.contextmanager
    def create_temp_dir(self, *args, **kwargs):
        """Creates a temporary folder and removes it later."""
        temp_dir = tempfile.mkdtemp(*args, **kwargs)
        try:
            yield temp_dir
        finally:
            shutil.rmtree(temp_dir)
