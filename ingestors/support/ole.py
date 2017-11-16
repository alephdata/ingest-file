import logging
from olefile import isOleFile, OleFileIO

log = logging.getLogger(__name__)


class OLESupport(object):
    """Provides helpers for Microsoft OLE files."""

    def ole_extract_metadata(self, file_path):
        with open(file_path, 'r') as fh:
            if not isOleFile(fh):
                return
            fh.seek(0)
            ole = OleFileIO(fh)
            self.olefileio_extract_metadata(ole)

    def olefileio_extract_metadata(self, ole):
        if not self.result.created_at:
            self.result.created_at = ole.root.getctime()
        if not self.result.modified_at:
            self.result.modified_at = ole.root.getmtime()

        meta = ole.get_metadata()

        if not self.result.title:
            self.result.title = meta.title
        if not self.result.title:
            self.result.title = meta.subject

        if not self.result.author:
            self.result.author = meta.author
        if not self.result.author:
            self.result.author = meta.last_saved_by

        if not self.result.summary:
            self.result.summary = meta.notes

        if not self.result.generator:
            self.result.generator = meta.creating_application

        if meta.company:
            self.result.entities.append(meta.company)

        if meta.language:
            self.result.languages.append(meta.language)

        if meta.keywords:
            self.result.keywords.append(meta.keywords)

        if not self.result.created_at:
            self.result.created_at = meta.create_time

        if not self.result.modified_at:
            self.result.modified_at = meta.last_saved_time

        # from pprint import pprint
        # pprint(self.result.to_dict())
