from __future__ import unicode_literals

import six
import rfc822
import logging
from time import mktime
from datetime import datetime
from flanker.addresslib import address
from normality import stringify, safe_filename

from ingestors.support.html import HTMLSupport
from ingestors.support.temp import TempFileSupport
from ingestors.support.plain import PlainTextSupport
from ingestors.util import join_path

log = logging.getLogger(__name__)


class EmailSupport(TempFileSupport, HTMLSupport, PlainTextSupport):
    """Extract metadata from email messages."""

    def ingest_attachment(self, name, mime_type, body, temp_dir):
        has_body = body is not None and len(body)
        if stringify(name) is None and not has_body:
            # Hello, Outlook.
            return

        file_name = safe_filename(name, default='attachment')
        name = stringify(name) or file_name
        foreign_id = join_path(self.result.id, name)

        file_path = join_path(temp_dir, file_name)
        with open(file_path, 'w') as fh:
            if isinstance(body, six.text_type):
                body = body.encode('utf-8')
            if body is not None:
                fh.write(body)

        self.manager.handle_child(self.result, file_path,
                                  id=foreign_id,
                                  file_name=name,
                                  mime_type=mime_type)

    def extract_headers_metadata(self, headers):
        headers = [(stringify(k), stringify(v)) for k, v in headers]
        self.result.headers = dict(headers)
        for field, value in headers:
            field = field.lower()
            if field is None or value is None:
                continue

            if field == 'subject':
                self.update('title', value)

            if field == 'message-id':
                self.update('id', value)

            if field == 'date':
                try:
                    date = rfc822.parsedate(value)
                    date = datetime.fromtimestamp(mktime(date))
                    self.update('created_at', date)
                except Exception as ex:
                    log.warning("Failed to parse [%s]: %s", date, ex)

            if field == 'from':
                addr = address.parse(value)
                if addr is not None:
                    author = stringify(addr.display_name)
                    email = stringify(addr.address)
                    self.result.emails.append(email)
                    if author is not None and author != email:
                        self.update('author', author)
                        self.result.entities.append(author)

            if field in ['to', 'cc', 'bcc']:
                for addr in address.parse_list(value):
                    name = stringify(addr.display_name)
                    email = stringify(addr.address)
                    self.result.emails.append(email)
                    if name is not None and name != email:
                        self.result.entities.append(name)
