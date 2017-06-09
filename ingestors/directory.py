import os

from ingestors.base import Ingestor
from ingestors.exc import ProcessingException
from ingestors.util import join_path, decode_path


class DirectoryIngestor(Ingestor):
    """Traverse the entries in a directory."""
    MIME_TYPE = "inode/directory"

    SKIP_ENTRIES = [
        '.git',
        '.hg',
        '.DS_Store',
        '.gitignore',
        'Thumbs.db',
        '__MACOSX'
    ]

    def ingest(self, file_path):
        """Ingestor implementation."""
        if not os.path.isdir(file_path):
            raise ProcessingException("Not a directory.")

        for name in os.listdir(file_path):
            name = decode_path(name)
            if name in self.SKIP_ENTRIES:
                continue
            sub_path = join_path(file_path, name)
            self.manager.handle_child(self.result, sub_path)
