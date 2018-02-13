import os
import time
import logging
import requests
import threading
from celestial import DEFAULT
from requests.exceptions import RequestException

from ingestors.exc import ConfigurationException, ProcessingException
from ingestors.util import join_path

log = logging.getLogger(__name__)


class UnoconvSupport(object):
    """Provides helpers for unconv via HTTP."""

    def get_unoconv_url(self):
        return self.manager.get_env('UNOSERVICE_URL')

    def is_unoconv_available(self):
        return self.get_unoconv_url() is not None

    @property
    def unoconv(self):
        if not hasattr(self, '_unoconv_client'):
            self._unoconv_client = threading.local()
        if not hasattr(self._unoconv_client, 'session'):
            self._unoconv_client.session = requests.Session()
        return self._unoconv_client.session

    def unoconv_to_pdf(self, file_path, retry=6):
        """Converts an office document to PDF."""
        if not self.is_unoconv_available():
            raise ConfigurationException("UNOSERVICE_URL is missing.")

        log.info('Converting [%s] to PDF...', self.result)
        file_name = os.path.basename(file_path)
        out_path = join_path(self.work_path, '%s.pdf' % file_name)
        for attempt in range(1, retry):
            try:
                with open(file_path, 'rb') as fh:
                    files = {'file': (file_name, fh, DEFAULT)}
                    res = self.unoconv.post(self.get_unoconv_url(),
                                            files=files,
                                            timeout=3600,
                                            stream=True)

                res.raise_for_status()
                length = 0
                with open(out_path, 'w') as fh:
                    for chunk in res.iter_content(chunk_size=None):
                        length += len(chunk)
                        fh.write(chunk)

                if length == 0:
                    raise ProcessingException("Could not convert to PDF.")
                return out_path
            except RequestException:
                log.exception("unoservice failed (attempt: %s)", attempt)
                time.sleep(3)

        raise ConfigurationException("PDF conversion service has failed.")
