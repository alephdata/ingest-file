import logging
import os

import pypff

from ingestors.base import Ingestor
from ingestors.support.temp import TempFileSupport
from ingestors.support.outlookpst import OutlookPSTSupport
from ingestors.support.ole import OLESupport
from ingestors.directory import DirectoryIngestor
from ingestors.util import join_path


log = logging.getLogger(__name__)


class OutlookPSTIngestor(Ingestor, TempFileSupport,
                         OutlookPSTSupport, OLESupport):
    MIME_DEFAULT = 'application/vnd.ms-outlook'
    MIME_TYPES = [MIME_DEFAULT]
    EXTENSIONS = ['pst', 'ost', 'pab']
    BASE_SCORE = 5
    COMMAND_TIMEOUT = 12 * 60 * 60

    def ingest(self, file_path):
        self.extract_ole_metadata(file_path)
        self.result.flag(self.result.FLAG_PACKAGE)
        temp_dir = self.make_empty_directory()
        try:
            pst_file = pypff.open(file_path)
            root = pst_file.get_root_folder()
            root_folder_name = root.name or os.path.basename(file_path)
            root_folder_path = os.path.join(temp_dir, root_folder_name)
            os.makedirs(root_folder_path)
            self.folder_traverse(root, root_folder_path)
            self.check_for_messages(root, root_folder_path)
            self.manager.delegate(DirectoryIngestor, self.result, temp_dir)
        except Exception:
            # Handle partially extracted archives.
            self.manager.delegate(DirectoryIngestor, self.result, temp_dir)
            raise
