from __future__ import unicode_literals

import os
import time
import shutil
import logging
import zipfile
from lxml import etree
from email import utils
from banal import clean_dict
from datetime import datetime
from normality import stringify

from ingestors.base import Ingestor
from ingestors.support.email import EmailSupport
from ingestors.support.temp import TempFileSupport
from ingestors.exc import ProcessingException

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
        base_name = os.path.basename(name)
        out_file = os.path.join(temp_dir, base_name)
        with open(out_file, 'w+b') as outfh:
            with zipf.open(name) as infh:
                shutil.copyfileobj(infh, outfh)
        return out_file

    def extract_hierarchy(self, name):
        result = self.result
        foreign_id = self.result.id
        path = os.path.dirname(name)
        for name in path.split(os.sep):
            foreign_id = os.path.join(foreign_id, name)
            if name in self.EXCLUDE:
                continue
            result = self.manager.handle_child(result, None,
                                               id=foreign_id,
                                               file_name=name)
        return result

    def extract_attachment(self, zipf, message, attachment, temp_dir):
        name = attachment.get('OPFAttachmentName')
        mime_type = attachment.get('OPFAttachmentContentType')
        url = attachment.get('OPFAttachmentURL')
        foreign_id = os.path.join(self.result.id, url)
        file_path = self.extract_file(zipf, url, temp_dir)
        self.manager.handle_child(message,
                                  file_path,
                                  id=foreign_id,
                                  file_name=name,
                                  mime_type=mime_type)


    def extract_message(self, zipf, name):
        parent = self.extract_hierarchy(name)
        with self.create_temp_dir() as temp_dir:
            xml_path = self.extract_file(zipf, name, temp_dir)
            foreign_id = os.path.join(self.result.id, name)
            message = self.manager.handle_child(parent,
                                                xml_path,
                                                id=foreign_id,
                                                mime_type=MIME)
            try:
                doc = self.parse_xml(xml_path)
                for el in doc.findall('.//messageAttachment'):
                    self.extract_attachment(zipf, message, el, temp_dir)
            except TypeError:
                pass # this will be reported for the individual file.

    def ingest(self, file_path):
        self.result.flag(self.result.FLAG_PACKAGE)
        try:
            with zipfile.ZipFile(file_path, 'r') as zipf:
                for name in zipf.namelist():
                    if 'message_' in name and name.endswith('.xml'):
                        self.extract_message(zipf, name)
        except zipfile.BadZipfile as bzfe:
            raise ProcessingException('Invalid OLM file.')


class OutlookOLMMessageIngestor(Ingestor, OPFParser, EmailSupport):
    MIME_TYPES = [MIME]
    EXTENSIONS = []
    SCORE = 15

    def get_contacts(self, doc, tag, display=False):
        emails = []
        path = './%s/emailAddress' % tag
        for address in doc.findall(path):
            email = address.get('OPFContactEmailAddressAddress')
            self.result.emails.append(email)
            name = address.get('OPFContactEmailAddressName')
            if name is not None and name != email:
                self.result.entities.append(name)
                if email is not None and not display:
                    email = '%s <%s>' % (name, email)
                else:
                    email = name
            if email is not None:
                emails.append(email)
    
        if len(emails):
            return ', '.join(emails)

    def ingest(self, file_path):
        self.result.flag(self.result.FLAG_EMAIL)
        try:
            doc = self.parse_xml(file_path)
        except TypeError:
            raise ProcessingException("Cannot parse OPF XML file.")
        
        if len(doc.findall('//email')) != 1:
            raise ProcessingException("More than one email in file.")
        
        email = doc.find('//email')
        props = {c.tag: c.text.strip() for c in email.getchildren() if c.text}
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

        self.result.headers = clean_dict(headers)

        self.update('title', props.pop('OPFMessageCopySubject', None))
        self.update('title', props.pop('OPFMessageCopyThreadTopic', None))
        self.update('author', self.get_contacts(email,
                                                'OPFMessageCopyFromAddresses',
                                                display=True))
        self.update('author', self.get_contacts(email,
                                                'OPFMessageCopySenderAddress',
                                                display=True))
        self.update('summary', props.pop('OPFMessageCopyPreview', None))
        self.update('created_at', props.pop('OPFMessageCopySentTime', None))
        self.update('modified_at', props.pop('OPFMessageCopyModDate', None))

        body = props.pop('OPFMessageCopyBody', None)
        html = props.pop('OPFMessageCopyHTMLBody', None)
        if '1E0' == props.pop('OPFMessageGetHasHTML', None) and stringify(html):
            self.extract_html_content(html)
            self.result.flag(self.result.FLAG_HTML)
        else:
            self.extract_plain_text_content(body)
            self.result.flag(self.result.FLAG_PLAINTEXT)
