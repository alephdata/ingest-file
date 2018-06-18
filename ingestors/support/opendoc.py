import logging
from datetime import datetime
from odf.opendocument import load

from ingestors.exc import ProcessingException

log = logging.getLogger(__name__)


class OpenDocumentSupport(object):
    """Provides helpers for Libre/Open Office tools."""

    def parse_odf_date(self, date):
        try:
            return datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            return None

    def parse_opendocument(self, file_path):
        try:
            doc = load(file_path)
        except Exception:
            raise ProcessingException("Cannot open document.")

        for child in doc.meta.childNodes:
            value = str(child)
            if child.tagName == 'dc:title':
                self.update('title', value)
            if child.tagName == 'dc:description':
                self.update('summary', value)
            if child.tagName == 'dc:creator':
                self.update('author', value)
            if child.tagName == 'dc:date':
                self.update('date', self.parse_odf_date(value))
            if child.tagName == 'meta:creation-date':
                self.update('created_at', self.parse_odf_date(value))
            if child.tagName == 'meta:generator':
                self.update('generator', value)

        # from pprint import pprint
        # pprint(self.result.to_dict())
        return doc
