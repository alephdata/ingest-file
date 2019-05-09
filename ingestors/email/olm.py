from __future__ import unicode_literals

import os
import time
import shutil
import logging
import zipfile
from lxml import etree
from email import utils
from datetime import datetime
from normality import safe_filename
from followthemoney import model

from ingestors.ingestor import Ingestor
from ingestors.support.email import EmailSupport
from ingestors.support.temp import TempFileSupport
from ingestors.exc import ProcessingException
from ingestors.util import safe_string
from ingestors.util import remove_directory

log = logging.getLogger(__name__)
MIME = 'application/xml+opfmessage'


class OPFParser(object):

    def parse_xml(self, file_path):
        parser = etree.XMLParser(huge_tree=True)
        try:
            return etree.parse(file_path, parser)
        except etree.XMLSyntaxError:
            # probably corrupt
            raise TypeError()


class OutlookOLMArchiveIngestor(Ingestor, TempFileSupport, OPFParser):
    MIME_TYPES = []
    EXTENSIONS = ['olm']
    SCORE = 10
    EXCLUDE = ['com.microsoft.__Messages']

    def extract_file(self, zipf, name, temp_dir):
        base_name = safe_filename(os.path.basename(name))
        out_file = os.path.join(temp_dir, base_name)
        with open(out_file, 'w+b') as outfh:
            try:
                with zipf.open(name) as infh:
                    shutil.copyfileobj(infh, outfh)
            except KeyError:
                log.warning("Cannot load zip member: %s", name)
        return out_file

    def extract_hierarchy(self, name, entity):
        foreign_id = entity.id
        path = os.path.dirname(name)
        for name in path.split(os.sep):
            foreign_id = os.path.join(foreign_id, name)
            if name in self.EXCLUDE:
                continue
            if foreign_id in self._hierarchy:
                result = self._hierarchy.get(foreign_id)
            else:
                result = self.manager.make_entity('Document', parent=entity)
                result.make_id(entity.id, name)
                self._hierarchy[foreign_id] = result
        return result

    def extract_attachment(self, zipf, message, attachment, temp_dir):
        url = attachment.get('OPFAttachmentURL')
        name = attachment.get('OPFAttachmentName')
        name = name or attachment.get('OPFAttachmentContentID')
        mime_type = attachment.get('OPFAttachmentContentType')
        child = self.manager.make_entity('Document', parent=message)
        child.add('mimeType', mime_type)
        if url is None and name is None:
            return
        if url is not None:
            file_path = self.extract_file(zipf, url, temp_dir)
            child.make_id(message.id, url)
        else:
            file_path = os.path.join(temp_dir, safe_filename(name))
            fh = open(file_path, 'w')
            fh.close()
            child.make_id(message.id, name)
        self.manager.handle_child(file_path, child)

    def extract_message(self, entity, zipf, name):
        if 'message_' not in name or not name.endswith('.xml'):
            return
        parent = self.extract_hierarchy(name, entity)
        message_dir = self.make_empty_directory()
        try:
            xml_path = self.extract_file(zipf, name, message_dir)
            child = self.manager.make_entity('Document', parent=parent)
            child.make_id(entity.id, parent.id, name)
            child.add('mimeType', MIME)
            self.manager.handle_child(xml_path, child)
            try:
                doc = self.parse_xml(xml_path)
                for el in doc.findall('.//messageAttachment'):
                    self.extract_attachment(zipf, child, el, message_dir)
            except TypeError:
                pass  # this will be reported for the individual file.
        finally:
            remove_directory(message_dir)

    def ingest(self, file_path, entity):
        entity.schema = model.get('Package')
        self._hierarchy = {}
        try:
            with zipfile.ZipFile(file_path, 'r') as zipf:
                for name in zipf.namelist():
                    try:
                        self.extract_message(entity, zipf, name)
                    except Exception:
                        log.exception('Error processing message: %s', name)
        except zipfile.BadZipfile:
            raise ProcessingException('Invalid OLM file.')


class OutlookOLMMessageIngestor(Ingestor, OPFParser, EmailSupport):
    MIME_TYPES = [MIME]
    EXTENSIONS = []
    SCORE = 15

    def get_email_addresses(self, doc, tag):
        path = './%s/emailAddress' % tag
        for address in doc.findall(path):
            email = safe_string(address.get('OPFContactEmailAddressAddress'))
            if not self.check_email(email):
                email = None
            self.result.emit_email(email)
            name = safe_string(address.get('OPFContactEmailAddressName'))
            if self.check_email(name):
                name = None
            if name or email:
                yield (name, email)

    def get_contacts(self, doc, tag, display=False):
        emails = []
        for (name, email) in self.get_email_addresses(doc, tag):
            if name is None:
                emails.append(email)
            elif email is None:
                emails.append(name)
            else:
                emails.append('%s <%s>' % (name, email))

        if len(emails):
            return '; '.join(emails)

    def get_contact_name(self, doc, tag):
        for (name, email) in self.get_email_addresses(doc, tag):
            if name is not None:
                return name

    def ingest(self, file_path, entity):
        entity.schema = model.get('Email')
        try:
            doc = self.parse_xml(file_path)
        except TypeError:
            raise ProcessingException("Cannot parse OPF XML file.")

        if len(doc.findall('//email')) != 1:
            raise ProcessingException("More than one email in file.")

        email = doc.find('//email')
        props = email.getchildren()
        props = {c.tag: safe_string(c.text) for c in props if c.text}
        headers = {
            'Subject': props.get('OPFMessageCopySubject'),
            'Message-ID': props.pop('OPFMessageCopyMessageID', None),
            'From': self.get_contacts(email, 'OPFMessageCopyFromAddresses'),
            'Sender': self.get_contacts(email, 'OPFMessageCopySenderAddress'),
            'To': self.get_contacts(email, 'OPFMessageCopyToAddresses'),
            'CC': self.get_contacts(email, 'OPFMessageCopyCCAddresses'),
            'BCC': self.get_contacts(email, 'OPFMessageCopyBCCAddresses'),
        }
        date = props.get('OPFMessageCopySentTime')
        if date is not None:
            date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
            date = time.mktime(date.timetuple())
            headers['Date'] = utils.formatdate(date)

        self.extract_headers_metadata(entity, headers)

        entity.add('title', props.pop('OPFMessageCopySubject', None))
        entity.add('title', props.pop('OPFMessageCopyThreadTopic', None))
        for tag in ('OPFMessageCopyFromAddresses',
                    'OPFMessageCopySenderAddress'):
            entity.add('author', self.get_contact_name(email, tag))

        entity.add('summary', props.pop('OPFMessageCopyPreview', None))
        entity.add('authoredAt', props.pop('OPFMessageCopySentTime', None))
        entity.add('modifiedAt', props.pop('OPFMessageCopyModDate', None))

        body = props.pop('OPFMessageCopyBody', None)
        html = props.pop('OPFMessageCopyHTMLBody', None)

        has_html = '1E0' == props.pop('OPFMessageGetHasHTML', None)
        if has_html and safe_string(html):
            self.extract_html_content(entity, html)
        else:
            entity.add('bodyText', body)
