import bz2
import gzip
import py7zr
import shutil
import tarfile
from pathlib import PurePath
from py7zr.exceptions import ArchiveError

from ingestors.ingestor import Ingestor
from ingestors.support.package import PackageSupport
from ingestors.support.shell import ShellSupport
from ingestors.exc import ProcessingException


class SevenZipIngestor(PackageSupport, Ingestor, ShellSupport):
    MIME_TYPES = ["application/x-7z-compressed", "application/7z-compressed"]
    EXTENSIONS = ["7z", "7zip"]
    SCORE = 4

    def unpack(self, file_path, entity, temp_dir):
        # check if the file_path belongs to a 7z fragmented archive and reconstruct the filename
        pure_file_path = PurePath(file_path)
        if "_7z" in pure_file_path.parts[-1]:
            reconstructed_filename = pure_file_path.parts[-1].replace("_7z", ".7z")
            pure_file_path = PurePath("/").joinpath(
                *pure_file_path.parts[1:-1], reconstructed_filename
            )

        try:
            with py7zr.SevenZipFile(str(pure_file_path), mode='r') as extractor:
                extractor.extractall(path=temp_dir)
        except ArchiveError as e:
            raise ProcessingException(f"Error: {e}")


class SingleFilePackageIngestor(PackageSupport, Ingestor):
    SCORE = 2

    def unpack(self, file_path, entity, temp_dir):
        file_name = entity.first("fileName") or "extracted"
        for ext in self.EXTENSIONS:
            ext = "." + ext
            if file_name.endswith(ext):
                file_name = file_name[: len(file_name) - len(ext)]
        temp_file = self.make_work_file(file_name, prefix=temp_dir)
        self.unpack_file(file_path, temp_file)

    def unpack_file(self, file_path, temp_file):
        raise NotImplementedError

    @classmethod
    def match(cls, file_path, entity):
        if tarfile.is_tarfile(file_path):
            return -1
        return super(SingleFilePackageIngestor, cls).match(file_path, entity)


class GzipIngestor(SingleFilePackageIngestor):
    MIME_TYPES = ["application/gzip", "application/x-gzip", "multipart/x-gzip"]
    EXTENSIONS = ["gz", "tgz"]

    def unpack_file(self, file_path, temp_file):
        try:
            with gzip.GzipFile(file_path) as src:
                with open(temp_file, "wb") as dst:
                    shutil.copyfileobj(src, dst)
        except IOError as ioe:
            raise ProcessingException("Error: %s" % ioe)


class BZ2Ingestor(SingleFilePackageIngestor):
    MIME_TYPES = [
        "application/x-bzip",
        "application/x-bzip2",
        "multipart/x-bzip",
        "multipart/x-bzip2",
    ]
    EXTENSIONS = ["bz", "tbz", "bz2", "tbz2"]

    def unpack_file(self, file_path, temp_file):
        try:
            with bz2.BZ2File(file_path) as src:
                with open(temp_file, "wb") as dst:
                    shutil.copyfileobj(src, dst)
        except IOError as ioe:
            raise ProcessingException("Error: %s" % ioe)
