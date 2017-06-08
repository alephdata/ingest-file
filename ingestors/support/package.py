import os
import six
import logging
import rarfile
import shutil
from chardet.universaldetector import UniversalDetector

from ingestors.support.temp import TempFileSupport
from ingestors.support.encoding import EncodingSupport
from ingestors.directory import DirectoryIngestor

log = logging.getLogger(__name__)


class PackageSupport(TempFileSupport, EncodingSupport):

    def unpack_members(self, pack, temp_dir):
        # Some archives come with non-Unicode file names, this
        # attempts to avoid that issue by naming the destination
        # explicitly.
        detector = UniversalDetector()
        for name in pack.namelist():
            if isinstance(name, six.binary_type):
                detector.feed(name)
            if detector.done:
                break

        detector.close()
        encoding = detector.result.get('encoding')
        encoding = self._normalize_encoding(encoding)

        log.debug('Detected filename encoding: %s', encoding)

        for name in pack.namelist():
            file_name = name
            if isinstance(name, six.binary_type):
                file_name = name.decode(encoding, 'ignore')

            out_path = os.path.join(temp_dir, file_name)
            if os.path.exists(out_path) or not out_path.startswith(temp_dir):
                continue

            out_dir = os.path.dirname(out_path)
            if not os.path.exists(out_dir):
                os.makedirs(out_dir)

            try:
                in_fh = pack.open(name)
                try:
                    log.debug("Unpack: %s -> %s", self.result.label, file_name)
                    with open(out_path, 'w') as out_fh:
                        shutil.copyfileobj(in_fh, out_fh)
                finally:
                    in_fh.close()
            except Exception as ex:
                # TODO: should this be a fatal error?
                log.debug("Failed to unpack %s: %s", out_path, ex)

    def ingest(self, file_path):
        # Work-around: try to unpack multi-part files by changing into
        # the directory containing the file.
        prev_cwd = os.getcwd()
        os.chdir(os.path.dirname(file_path))
        with self.create_temp_dir() as temp_dir:
            try:
                log.info("Descending into package: %r", self.result.label)
                self.unpack(file_path, temp_dir)
                self.manager.delegate(DirectoryIngestor, self.result, temp_dir)
            except rarfile.NeedFirstVolume:
                pass
            finally:
                os.chdir(prev_cwd)

    def unpack(self, file_path, temp_dir):
        pass
