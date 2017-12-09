import logging
from olefile import isOleFile, OleFileIO

log = logging.getLogger(__name__)


class OLESupport(object):
    """Provides helpers for Microsoft OLE files."""

    def extract_ole_metadata(self, file_path):
        with open(file_path, 'r') as fh:
            if not isOleFile(fh):
                return
            fh.seek(0)
            ole = OleFileIO(fh)
            self.extract_olefileio_metadata(ole)

    def extract_olefileio_metadata(self, ole):
        self.update('created_at', ole.root.getctime())
        self.update('modified_at', ole.root.getmtime())

        meta = ole.get_metadata()
        self.update('title', meta.title)
        # self.update('title', meta.subject)
        self.update('author', meta.author)
        self.update('author', meta.last_saved_by)
        self.update('summary', meta.notes)
        self.update('generator', meta.creating_application)
        self.update('created_at', meta.create_time)
        self.update('modified_at', meta.last_saved_time)

        if meta.company:
            self.result.entities.append(meta.company)

        if meta.language:
            self.result.languages.append(meta.language)

        if meta.keywords:
            self.result.keywords.append(meta.keywords)

        # from pprint import pprint
        # pprint(self.result.to_dict())
