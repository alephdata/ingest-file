import logging
from lxml import etree
from datetime import datetime
from zipfile import ZipFile, BadZipfile

# from ingestors.exc import ProcessingException

log = logging.getLogger(__name__)


class OOXMLSupport(object):
    """Provides helpers for Office Open XML format metadata."""
    PROP_FILE = 'docProps/core.xml'
    CP_NS = '{http://schemas.openxmlformats.org/package/2006/metadata/core-properties}'  # noqa
    DC_NS = '{http://purl.org/dc/elements/1.1/}'  # noqa
    DCT_NS = '{http://purl.org/dc/terms/}'  # noqa

    def parse_ooxml_date(self, date):
        try:
            return datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
        except ValueError:
            return None

    def parse_ooxml_core(self, file_path):
        try:
            with ZipFile(file_path) as zf:
                zf.getinfo(self.PROP_FILE)
                with zf.open(self.PROP_FILE, 'r') as xml:
                    return etree.parse(xml)
        except KeyError:  # missing the PROP_FILE
            return None
        except BadZipfile:
            return None

    def ooxml_extract_metadata(self, file_path):
        doc = self.parse_ooxml_core(file_path)
        if doc is None:
            # TODO: should this trigger a ProcessingExc on the whole doc?
            return
        # print etree.tostring(doc, pretty_print=True)

        def get(ns, name):
            return doc.findtext('.//%s%s' % (ns, name))

        self.update('title', get(self.DC_NS, 'title'))
        self.update('title', get(self.DC_NS, 'subject'))
        self.update('summary', get(self.DC_NS, 'description'))
        self.update('author', get(self.DC_NS, 'creator'))
        self.update('author', get(self.CP_NS, 'lastModifiedBy'))

        created_at = self.parse_ooxml_date(get(self.DCT_NS, 'created'))
        self.update('created_at', created_at)

        modified_at = self.parse_ooxml_date(get(self.DCT_NS, 'modified'))
        self.update('modified_at', modified_at)
        # from pprint import pprint
        # pprint(self.result.to_dict())
