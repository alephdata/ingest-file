from ingestors.base import Ingestor
from ingestors.support.temp import TempFileSupport
from ingestors.support.shell import ShellSupport
from ingestors.directory import DirectoryIngestor


class OutlookPSTIngestor(Ingestor, TempFileSupport, ShellSupport):
    MIME_TYPES = ['application/vnd.ms-outlook']
    EXTENSIONS = ['pst', 'ost']
    BASE_SCORE = 5
    COMMAND_TIMEOUT = 12 * 60 * 60

    def ingest(self, file_path):
        with self.create_temp_dir() as temp_dir:
            if self.result.mime_type is None:
                self.result.mime_type = self.MIME_TYPES[0]
            self.exec_command('readpst',
                              '-M',  # make subfolders, files per message
                              '-D',  # include deleted
                              '-r',  # recursive structure
                              '-8',  # utf-8 where possible
                              '-b',
                              '-q',  # quiet
                              '-o', temp_dir,
                              file_path)
            self.manager.delegate(DirectoryIngestor, self.result, temp_dir)
