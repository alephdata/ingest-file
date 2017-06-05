import os

from ingestors.base import Ingestor


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
        for name in os.listdir(file_path):
            if name in self.SKIP_ENTRIES:
                continue
            sub_path = os.path.join(file_path, name)
            self.manager.handle_child(sub_path)
