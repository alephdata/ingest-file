import os
from ingestors.log import get_logger
from tempfile import gettempdir
from psutil import pid_exists

log = get_logger(__name__)


class FileLock:
    """Manage a lock file for the LO process."""

    def __init__(self):
        self.path = os.path.join(gettempdir(), "convert.lock")

    def lock(self):
        # Race conditions galore, but how likely
        # are requests at that rate?
        if self.is_locked:
            return False
        with open(self.path, "w") as handle:
            handle.write(str(os.getpid()))
        return True

    def unlock(self):
        if os.path.exists(self.path):
            os.unlink(self.path)

    @property
    def is_locked(self):
        try:
            with open(self.path, "r") as handle:
                pid = int(handle.read())
        except (ValueError, FileNotFoundError):
            return False
        if not pid_exists(pid):
            return False
        return True
