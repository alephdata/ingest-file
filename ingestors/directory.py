import os
from followthemoney import model

from ingestors.ingestor import Ingestor
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

    def ingest(self, file_path, entity):
        """Ingestor implementation."""
        entity.schema = model.get('Folder')
        file_path = decode_path(file_path)

        if file_path is None or not os.path.isdir(file_path):
            return

        for name in os.listdir(file_path):
            name = decode_path(name)
            if name in self.SKIP_ENTRIES:
                continue
            sub_path = join_path(file_path, name)
            child = self.manager.make_entity('Document')
            child.make_id(entity.id, name)
            child.add('fileName', name)
            child.set('parent', entity)
            self.manager.handle_child(sub_path, child)
