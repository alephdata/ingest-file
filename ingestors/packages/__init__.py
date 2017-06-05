import os
import logging
import shutil
import gzip
import bz2
import rarfile
import zipfile
import tarfile

from ingestors.base import Ingestor
from ingestors.support.shell import ShellSupport
from ingestors.support.package import PackageSupport

log = logging.getLogger(__name__)


class RARIngestor(PackageSupport, Ingestor):

    def unpack(self, file_path, temp_dir):
        with rarfile.RarFile(file_path) as rf:
            self.unpack_members(rf, temp_dir)

    @classmethod
    def match(cls, file_path, mime_type=None):
        if rarfile.is_rarfile(file_path):
            return 4
        return -1


class ZipIngestor(PackageSupport, Ingestor):

    def unpack(self, file_path, temp_dir):
        with zipfile.ZipFile(file_path) as zf:
            self.unpack_members(zf, temp_dir)

    @classmethod
    def match(cls, file_path, mime_type=None):
        if zipfile.is_zipfile(file_path):
            return 3
        return -1


class TarIngestor(PackageSupport, Ingestor):

    def unpack(self, file_path, temp_dir):
        with tarfile.open(name=file_path, mode='r:*') as tf:
            tf.extractall(temp_dir)

    @classmethod
    def match(cls, file_path, mime_type=None):
        if tarfile.is_tarfile(file_path):
            return 4
        return -1


class SevenZipIngestor(PackageSupport, Ingestor, ShellSupport):
    MIME_TYPES = ['application/x-7z-compressed']
    EXTENSIONS = ['7z', '7zip']
    SCORE = 4

    def unpack(self, file_path, temp_dir):
        self.exec_command('7z',
                          'x', file_path,
                          '-y',
                          '-r',
                          '-bb0',
                          '-bd',
                          '-oc:%s' % temp_dir)


class SingleFilePackageIngestor(PackageSupport, Ingestor):
    SCORE = 2

    def unpack(self, file_path, temp_dir):
        file_name = self.result.file_name
        for ext in self.EXTENSIONS:
            ext = '.' + ext
            if file_name.endswith(ext):
                file_name = file_name[:len(file_name) - len(ext)]
        temp_file = os.path.join(temp_dir, file_name)
        self.unpack_file(file_path, temp_file)

    @classmethod
    def match(cls, file_path, mime_type=None):
        if tarfile.is_tarfile(file_path):
            return -1
        return super(SingleFilePackageIngestor, cls).match(file_path,
                                                           mime_type=mime_type)


class GzipIngestor(SingleFilePackageIngestor):
    MIME_TYPES = ['application/x-gzip', 'multipart/x-gzip']
    EXTENSIONS = ['gz', 'tgz']

    def unpack_file(self, file_path, temp_file):
        with gzip.GzipFile(file_path) as src:
            with open(temp_file, 'wb') as dst:
                shutil.copyfileobj(src, dst)


class BZ2Ingestor(SingleFilePackageIngestor):
    MIME_TYPES = ['application/x-bzip', 'application/x-bzip2',
                  'multipart/x-bzip', 'multipart/x-bzip2']
    EXTENSIONS = ['bz', 'tbz', 'bz2', 'tbz2']

    def unpack_file(self, file_path, temp_file):
        with bz2.BZ2File(file_path) as src:
            with open(temp_file, 'wb') as dst:
                shutil.copyfileobj(src, dst)
