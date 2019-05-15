from __future__ import unicode_literals

import re
import email
import logging
from time import mktime
from datetime import datetime
from flanker.addresslib import address
from normality import safe_filename, stringify
from followthemoney.types import registry

from ingestors.support.html import HTMLSupport
from ingestors.support.temp import TempFileSupport
from ingestors.util import join_path, safe_string

log = logging.getLogger(__name__)

EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")


class EmailSupport(TempFileSupport, HTMLSupport):
    """Extract metadata from email messages."""

    def ingest_attachment(self, entity, name, mime_type, body):
        has_body = body is not None and len(body)
        if safe_string(name) is None and not has_body:
            # Hello, Outlook.
            return

        file_name = safe_filename(name, default='attachment')
        name = safe_string(name) or file_name
        child = self.manager.make_entity('Document', parent=entity)
        child.make_id(entity.id, name)

        file_path = join_path(self.work_path, file_name)
        with open(file_path, 'wb') as fh:
            if isinstance(body, str):
                body = body.encode('utf-8')
            if body is not None:
                fh.write(body)

        if isinstance(mime_type, bytes):
            mime_type = mime_type.decode('utf-8')
        child.add('mimeType', mime_type)

        self.manager.handle_child(file_path, child)

    def check_email(self, text):
        """Does it roughly look like an email?"""
        if text is None:
            return False
        if EMAIL_REGEX.match(text):
            return True
        return False

    def parse_emails(self, text, entity):
        """Parse an email list with the side effect of adding them to the
        relevant result lists."""
        parsed = address.parse_list(safe_string(text))

        # If the snippet didn't parse, assume it is just a name.
        if not len(parsed):
            return [(text, None)]

        values = []
        for addr in parsed:
            name = stringify(addr.display_name)
            email = stringify(addr.address)

            if not self.check_email(email):
                email = None

            if self.check_email(name):
                email = email or name
                name = None

            person = self.manager.make_entity('Person')
            person.make_id(entity.id, name, email)
            person.add('name', name)
            person.add('email', email)
            self.manager.emit_entity(person)
            entity.add('emailMentioned', email)
            entity.add('namesMentioned', name)
            values.append((name, email))
        return values

    def extract_headers_metadata(self, entity, headers):
        headers = dict(headers)
        entity.add('headers', registry.json.pack(dict(headers)))
        headers = [(safe_string(k), safe_string(v)) for k, v in headers.items()]  # noqa
        for field, value in headers:
            field = field.lower()

            if field == 'subject':
                entity.add('title', value)

            if field == 'message-id':
                entity.add('messageId', value)

            if field == 'in-reply-to':
                entity.add('inReplyTo', value)
            if field == 'references':
                for email_addr in value.split():
                    entity.add('inReplyTo', email_addr)

            if field == 'date':
                date = value
                try:
                    date = email.utils.parsedate(date)
                    date = datetime.fromtimestamp(mktime(date))
                    entity.add('authoredAt', date)
                except Exception as ex:
                    log.warning("Failed to parse [%s]: %s", date, ex)

            if field == 'from':
                for (name, _) in self.parse_emails(value, entity):
                    entity.add('author', name)

            if field in ['to', 'cc', 'bcc']:
                self.parse_emails(value, entity)
