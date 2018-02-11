from uuid import uuid4

from ingestors.util import make_directory


class TempFileSupport(object):
    """Provides helpers for file system related tasks."""

    def make_empty_directory(self):
        return make_directory(self.work_path, uuid4().hex)
