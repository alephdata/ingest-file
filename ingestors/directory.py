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
        file_path = decode_path(file_path)
        entity.schema = model.get('Folder')

        if file_path is None or not os.path.isdir(file_path):
            return

        self.crawl(self.manager, file_path, parent=entity)

    @classmethod
    def crawl(cls, manager, file_path, parent=None):
        for name in os.listdir(file_path):
            name = decode_path(name)
            if name in cls.SKIP_ENTRIES:
                continue
            sub_path = join_path(file_path, name)
            child = manager.make_entity('Document', parent=parent)
            child.add('fileName', name)
            if os.path.isdir(sub_path):
                if parent is not None:
                    child.make_id(parent.id, name)
                else:
                    child.make_id(name)
                child.schema = model.get('Folder')
                child.add('mimeType', cls.MIME_TYPE)
                manager.emit_entity(child)
                cls.crawl(manager, sub_path, parent=child)
            else:
                checksum = manager.archive_entity(child, sub_path)
                child.make_id(checksum)
                manager.queue_entity(child)
