import six
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
            value = six.text_type(child)
            if child.tagName == 'dc:title' and not self.result.title:
                self.result.title = value
            if child.tagName == 'dc:description' and not self.result.summary:
                self.result.summary = value
            if child.tagName == 'dc:creator' and not self.result.author:
                self.result.author = value
            if child.tagName == 'dc:date':
                if not self.result.date:
                    self.result.date = self.parse_odf_date(value)
            if child.tagName == 'meta:creation-date':
                if not self.result.created_at:
                    self.result.created_at = self.parse_odf_date(value)
            if child.tagName == 'meta:generator':
                self.result.generator = value

        # from pprint import pprint
        # pprint(self.result.to_dict())
        return doc
