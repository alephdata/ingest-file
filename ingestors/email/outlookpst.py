from ingestors.base import Ingestor
from ingestors.support.temp import TempFileSupport
from ingestors.support.shell import ShellSupport
from ingestors.support.ole import OLESupport
from ingestors.directory import DirectoryIngestor


class OutlookPSTIngestor(Ingestor, TempFileSupport, ShellSupport, OLESupport):
    MIME_DEFAULT = 'application/vnd.ms-outlook'
    MIME_TYPES = [MIME_DEFAULT]
    EXTENSIONS = ['pst', 'ost', 'pab']
    BASE_SCORE = 5
    COMMAND_TIMEOUT = 12 * 60 * 60

    def ingest(self, file_path):
        self.extract_ole_metadata(file_path)
        self.result.flag(self.result.FLAG_DIRECTORY)
        with self.create_temp_dir() as temp_dir:
            try:
                self.exec_command('readpst',
                                  '-e',  # make subfolders, files per message
                                  '-D',  # include deleted
                                  '-r',  # recursive structure
                                  '-8',  # utf-8 where possible
                                  '-b',
                                  '-q',  # quiet
                                  '-o', temp_dir,
                                  file_path)
                self.manager.delegate(DirectoryIngestor, self.result, temp_dir)
            except Exception:
                # Handle partially extracted archives.
                self.manager.delegate(DirectoryIngestor, self.result, temp_dir)
                raise
