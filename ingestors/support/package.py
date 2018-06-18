import os
import shutil
import logging

from ingestors.support.temp import TempFileSupport
from ingestors.support.encoding import EncodingSupport
from ingestors.directory import DirectoryIngestor
from ingestors.util import join_path, make_directory

log = logging.getLogger(__name__)


class PackageSupport(TempFileSupport, EncodingSupport):

    def ensure_path(self, base_dir, name, encoding='utf-8'):
        if isinstance(name, bytes):
            name = name.decode(encoding, 'ignore')

        out_path = join_path(base_dir, name)
        # out_path = os.path.normpath(out_path)
        if not out_path.startswith(base_dir):
            return
        if os.path.exists(out_path):
            return

        out_dir = os.path.dirname(out_path)
        make_directory(out_dir)
        if os.path.isdir(out_path):
            return

        return out_path

    def extract_member(self, base_dir, name, fh, encoding):
        out_path = self.ensure_path(base_dir, name, encoding=encoding)
        if out_path is None:
            return
        file_name = os.path.basename(out_path)
        try:
            log.debug("Unpack: %s -> %s", self.result, file_name)
            with open(out_path, 'wb') as out_fh:
                shutil.copyfileobj(fh, out_fh)
        finally:
            fh.close()

    def ingest(self, file_path):
        self.result.flag(self.result.FLAG_PACKAGE)
        temp_dir = self.make_empty_directory()
        self.unpack(file_path, temp_dir)
        self.manager.delegate(DirectoryIngestor, self.result, temp_dir)

    def unpack(self, file_path, temp_dir):
        pass
