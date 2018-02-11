from __future__ import unicode_literals

import re
import six
import rfc822
import logging
from time import mktime
from datetime import datetime
from flanker.addresslib import address
from normality import safe_filename, stringify

from ingestors.support.html import HTMLSupport
from ingestors.support.temp import TempFileSupport
from ingestors.support.plain import PlainTextSupport
from ingestors.util import join_path, safe_string, safe_dict

log = logging.getLogger(__name__)

EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")


class EmailSupport(TempFileSupport, HTMLSupport, PlainTextSupport):
    """Extract metadata from email messages."""

    def ingest_attachment(self, name, mime_type, body):
        has_body = body is not None and len(body)
        if safe_string(name) is None and not has_body:
            # Hello, Outlook.
            return

        file_name = safe_filename(name, default='attachment')
        name = safe_string(name) or file_name
        foreign_id = join_path(self.result.id, name)

        file_path = join_path(self.work_path, file_name)
        with open(file_path, 'w') as fh:
            if isinstance(body, six.text_type):
                body = body.encode('utf-8')
            if body is not None:
                fh.write(body)

        self.manager.handle_child(self.result, file_path,
                                  id=foreign_id,
                                  file_name=name,
                                  mime_type=mime_type)

    def check_email(self, text):
        """Does it roughly look like an email?"""
        if text is None:
            return False
        if EMAIL_REGEX.match(text):
            return True
        return False

    def parse_emails(self, text):
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

            self.result.emit_email(email)
            self.result.emit_name(name)
            values.append((name, email))
        return values

    def extract_headers_metadata(self, headers):
        self.result.headers = safe_dict(dict(headers))
        headers = [(safe_string(k), safe_string(v)) for k, v in headers]
        for field, value in headers:
            field = field.lower()
            if field is None or value is None:
                continue

            if field == 'subject':
                self.update('title', value)

            if field == 'message-id':
                self.update('message_id', value)

            if field == 'date':
                try:
                    date = rfc822.parsedate(value)
                    date = datetime.fromtimestamp(mktime(date))
                    self.update('created_at', date)
                except Exception as ex:
                    log.warning("Failed to parse [%s]: %s", date, ex)

            if field == 'from':
                for (name, _) in self.parse_emails(value):
                    self.update('author', name)

            if field in ['to', 'cc', 'bcc']:
                self.parse_emails(value)
