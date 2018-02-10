import os

from ingestors.base import Ingestor
from ingestors.util import join_path, decode_path


class DirectoryIngestor(Ingestor):
    """Traverse the entries in a directory."""
    MIME_TYPE = "inode/directory"

    SKIP_ENTRIES = [
        '.git',
        '.hg',
        '__MACOSX',
        '.gitignore'
    ]

    def ingest(self, file_path):
        """Ingestor implementation."""
        self.result.flag(self.result.FLAG_DIRECTORY)
        file_path = decode_path(file_path)

        if file_path is None or not os.path.isdir(file_path):
            return

        for name in os.listdir(file_path):
            name = decode_path(name)
            if name in self.SKIP_ENTRIES:
                continue
            sub_path = join_path(file_path, name)
            child_id = join_path(self.result.id, name)
            self.manager.handle_child(self.result,
                                      sub_path,
                                      file_name=name,
                                      id=child_id)
