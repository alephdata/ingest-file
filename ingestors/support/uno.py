import os
import time
import logging
import requests
from celestial import DEFAULT
from requests.exceptions import RequestException

from ingestors.exc import ConfigurationException, ProcessingException
from ingestors.util import join_path

log = logging.getLogger(__name__)


class UnoconvSupport(object):
    """Provides helpers for UNO document conversion via HTTP."""

    def get_unoconv_url(self):
        return self.manager.get_env('UNOSERVICE_URL')

    def is_unoconv_available(self):
        return self.get_unoconv_url() is not None

    def unoconv_to_pdf(self, file_path, retry=5):
        """Converts an office document to PDF."""
        if not self.is_unoconv_available():
            raise ConfigurationException("UNOSERVICE_URL is missing.")

        log.info('Converting [%s] to PDF...', self.result)
        out_path = os.path.basename(file_path)
        out_path = join_path(self.work_path, '%s.pdf' % out_path)
        file_name = self.result.file_name or 'data'
        mime_type = self.result.mime_type or DEFAULT
        attempt = 1
        while attempt <= retry:
            fh = open(file_path, 'rb')
            try:
                files = {'file': (file_name, fh, mime_type)}
                res = requests.post(self.get_unoconv_url(),
                                    files=files,
                                    timeout=(5, 305),
                                    stream=True)
            except RequestException as exc:
                log.warning("Conversion failed: %s", exc)
                time.sleep(2 ** attempt)
                attempt += 1
                continue
            finally:
                fh.close()

            if res.status_code == 400:
                raise ProcessingException(res.text)

            with open(out_path, 'wb') as fh:
                for chunk in res.iter_content(chunk_size=None):
                    fh.write(chunk)
            return out_path

        raise ProcessingException("Document could not be converted to PDF.")
