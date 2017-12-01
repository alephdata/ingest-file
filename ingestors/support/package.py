import os
import six
import shutil
import logging
import rarfile
from normality import guess_encoding

from ingestors.support.temp import TempFileSupport
from ingestors.support.encoding import EncodingSupport
from ingestors.directory import DirectoryIngestor
from ingestors.util import join_path, make_directory

log = logging.getLogger(__name__)


class PackageSupport(TempFileSupport, EncodingSupport):

    def unpack_members(self, pack, temp_dir):
        # Some archives come with non-Unicode file names, this
        # attempts to avoid that issue by naming the destination
        # explicitly.
        names = pack.namelist()
        names = [n for n in names if isinstance(n, six.binary_type)]
        encoding = guess_encoding('\n'.join(names))
        log.debug('Detected filename encoding: %s', encoding)

        for name in pack.namelist():
            file_name = name
            if isinstance(name, six.binary_type):
                file_name = name.decode(encoding, 'ignore')

            out_path = join_path(temp_dir, file_name)
            if os.path.exists(out_path):
                continue
            if not out_path.startswith(temp_dir):
                continue

            out_dir = os.path.dirname(out_path)
            make_directory(out_dir)
            if os.path.isdir(out_path):
                continue

            try:
                in_fh = pack.open(name)
                try:
                    log.debug("Unpack: %s -> %s", self.result, file_name)
                    with open(out_path, 'w') as out_fh:
                        shutil.copyfileobj(in_fh, out_fh)
                finally:
                    in_fh.close()
            except Exception as ex:
                # TODO: should this be a fatal error?
                log.debug("Failed to unpack [%s]: %s", file_name, ex)

    def ingest(self, file_path):
        self.result.flag(self.result.FLAG_PACKAGE)
        with self.create_temp_dir() as temp_dir:
            try:
                log.info("Descending: %s", self.result)
                self.unpack(file_path, temp_dir)
                self.manager.delegate(DirectoryIngestor, self.result, temp_dir)
            except rarfile.NeedFirstVolume:
                pass

    def unpack(self, file_path, temp_dir):
        pass
