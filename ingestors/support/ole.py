import logging
from olefile import isOleFile, OleFileIO

log = logging.getLogger(__name__)


class OLESupport(object):
    """Provides helpers for Microsoft OLE files."""

    def extract_ole_metadata(self, file_path):
        with open(file_path, 'rb') as fh:
            if not isOleFile(fh):
                return
            fh.seek(0)
            try:
                ole = OleFileIO(fh)
                self.extract_olefileio_metadata(ole)
            except (RuntimeError, IOError):
                # OLE reading can go fully recursive, at which point it's OK
                # to just eat this runtime error quietly.
                log.warning("Failed to read OLE data: %s", self.result)
            except Exception:
                log.exception("Failed to read OLE data: %s", self.result)

    def extract_olefileio_metadata(self, ole):
        try:
            self.update('created_at', ole.root.getctime())
        except Exception:
            log.warning("Failed to parse OLE ctime.")
        try:
            self.update('modified_at', ole.root.getmtime())
        except Exception:
            log.warning("Failed to parse OLE mtime.")

        try:
            meta = ole.get_metadata()
            self.update('title', meta.title)
            self.update('author', meta.author)
            self.update('author', meta.last_saved_by)
            self.update('summary', meta.notes)
            self.update('generator', meta.creating_application)
            self.update('created_at', meta.create_time)
            self.update('modified_at', meta.last_saved_time)
            self.result.emit_name(meta.company)
            self.result.emit_language(meta.language)
            # self.result.emit_keyword(meta.keywords)

        except Exception:
            log.exception("OLE parsing error.")

        # from pprint import pprint
        # pprint(self.result.to_dict())
