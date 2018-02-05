import shutil
import gzip
import bz2
import rarfile
import zipfile
import tarfile

from ingestors.base import Ingestor
from ingestors.support.shell import ShellSupport
from ingestors.support.package import PackageSupport
from ingestors.exc import ProcessingException
from ingestors.util import join_path


class RARIngestor(PackageSupport, Ingestor):
    MIME_TYPES = [
        'application/rar'
        'application/x-rar'
    ]
    EXTENSIONS = [
        'rar'
    ]
    SCORE = 4

    def unpack(self, file_path, temp_dir):
        # FIXME: need to figure out how to unpack multi-part files.
        try:
            with rarfile.RarFile(file_path) as rf:
                self.unpack_members(rf, temp_dir)
        except rarfile.Error as err:
            raise ProcessingException('Invalid RAR file: %s' % err)

    @classmethod
    def match(cls, file_path, result=None):
        if rarfile.is_rarfile(file_path):
            return cls.SCORE
        return super(RARIngestor, cls).match(file_path, result=result)


class ZipIngestor(PackageSupport, Ingestor):
    MIME_TYPES = [
        'application/zip',
        'application/x-zip',
        'multipart/x-zip',
        'application/zip-compressed',
        'application/x-zip-compressed',
    ]
    EXTENSIONS = [
        'zip'
    ]
    SCORE = 3

    def unpack(self, file_path, temp_dir):
        try:
            with zipfile.ZipFile(file_path) as zf:
                self.unpack_members(zf, temp_dir)
        except zipfile.BadZipfile as bzfe:
            raise ProcessingException('Invalid ZIP file: %s' % bzfe)

    @classmethod
    def match(cls, file_path, result=None):
        if zipfile.is_zipfile(file_path):
            return cls.SCORE
        return super(ZipIngestor, cls).match(file_path, result=result)


class TarIngestor(PackageSupport, Ingestor):
    MIME_TYPES = [
        'application/tar',
        'application/x-tar',
        'application/x-tgz',
        'application/x-gtar'
    ]
    EXTENSIONS = [
        'tar'
    ]
    SCORE = 4

    def unpack(self, file_path, temp_dir):
        try:
            with tarfile.open(name=file_path, mode='r:*') as tf:
                tf.extractall(temp_dir)
        except tarfile.TarError as err:
            raise ProcessingException('Invalid Tar file: %s' % err)

    @classmethod
    def match(cls, file_path, result=None):
        if tarfile.is_tarfile(file_path):
            return cls.SCORE
        return super(TarIngestor, cls).match(file_path, result=result)


class SevenZipIngestor(PackageSupport, Ingestor, ShellSupport):
    MIME_TYPES = [
        'application/x-7z-compressed',
        'application/7z-compressed'
    ]
    EXTENSIONS = [
        '7z',
        '7zip'
    ]
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
        file_name = self.result.file_name or 'extracted'
        for ext in self.EXTENSIONS:
            ext = '.' + ext
            if file_name.endswith(ext):
                file_name = file_name[:len(file_name) - len(ext)]
        temp_file = join_path(temp_dir, file_name)
        self.unpack_file(file_path, temp_file)

    @classmethod
    def match(cls, file_path, result=None):
        if tarfile.is_tarfile(file_path):
            return -1
        return super(SingleFilePackageIngestor, cls).match(file_path,
                                                           result=result)


class GzipIngestor(SingleFilePackageIngestor):
    MIME_TYPES = [
        'application/gzip',
        'application/x-gzip',
        'multipart/x-gzip'
    ]
    EXTENSIONS = [
        'gz',
        'tgz'
    ]

    def unpack_file(self, file_path, temp_file):
        with gzip.GzipFile(file_path) as src:
            with open(temp_file, 'wb') as dst:
                shutil.copyfileobj(src, dst)


class BZ2Ingestor(SingleFilePackageIngestor):
    MIME_TYPES = [
        'application/x-bzip',
        'application/x-bzip2',
        'multipart/x-bzip',
        'multipart/x-bzip2'
    ]
    EXTENSIONS = [
        'bz',
        'tbz',
        'bz2',
        'tbz2'
    ]

    def unpack_file(self, file_path, temp_file):
        with bz2.BZ2File(file_path) as src:
            with open(temp_file, 'wb') as dst:
                shutil.copyfileobj(src, dst)
