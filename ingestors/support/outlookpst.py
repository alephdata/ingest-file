import os
import logging
from email.message import EmailMessage
from email.parser import Parser
from email import policy

import magic

from ingestors.util import safe_path

log = logging.getLogger(__name__)


class OutlookPSTSupport(object):
    """Provides helpers for parsing outlook data files (pst, ost etc)."""

    def folder_traverse(self, parent_folder, parent_path):
        for folder in parent_folder.sub_folders:
            if not folder.name:
                continue
            new_path = os.path.join(parent_path, safe_path(folder.name))
            if folder.number_of_sub_folders:
                self.folder_traverse(folder, new_path)
            self.check_for_messages(folder, new_path)

    def handle_email_message(self, message, folder_path):
        file_path = os.path.join(
            folder_path, safe_path(message.subject) + '.email'
        )
        msg = EmailMessage()
        if message.plain_text_body:
            msg.set_content(
                message.plain_text_body, maintype='text', subtype='plain'
            )
        if message.html_body:
            msg.add_alternative(
                message.html_body, maintype='text', subtype='html'
            )
        headers = Parser(policy=policy.default).parsestr(
            message.transport_headers, headersonly=True
        )
        for key, val in headers.items():
            if key not in msg:
                msg.add_header(key, val)
        for index, attachment in enumerate(message.attachments):
            name = attachment.name or "attachment-{0}".format(index)
            attachment_buffer = attachment.read_buffer(attachment.size)
            ctype = magic.from_buffer(attachment_buffer, mime=True)
            maintype, subtype = ctype.split('/', 1)
            msg.add_attachment(
                attachment_buffer, maintype=maintype,
                subtype=subtype, filename=name)
        if not os.path.isdir(folder_path):
            os.makedirs(folder_path)
        with open(file_path, 'wb') as fp:
            fp.write(msg.as_bytes(policy=policy.default))


    def handle_text_message(self, message, folder_path):
        file_path = os.path.join(folder_path, safe_path(message.subject))
        if not os.path.isdir(folder_path):
            os.makedirs(folder_path)
        with open(file_path, 'wb') as fp:
            if message.html_body:
                fp.write(message.html_body)
            elif message.plain_text_body:
                fp.write(message.plain_text_body)
            elif message.rtf_body:
                fp.write(message.rtf_body)
        for index, attachment in enumerate(message.attachments):
            name = attachment.name or "attachment-{0}".format(index)
            attachment_path = os.path.join(folder_path, safe_path(name))
            with open(attachment_path, 'wb') as fp:
                fp.write(attachment.read_buffer(attachment.size))


    def check_for_messages(self, folder, folder_path):
        for message in folder.sub_messages:
            if not message.subject:
                continue
            if message.transport_headers:
                self.handle_email_message(message, folder_path)
            else:
                self.handle_text_message(message, folder_path)
