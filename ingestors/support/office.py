import os.path
import logging
import subprocess32 as subprocess
from distutils.spawn import find_executable


class OfficeSupport(object):
    """Provides helpers for Libre/Open Office tools."""

    logger = logging.getLogger(__name__)

    #: Convertion time before the job gets cancelled.
    CONVERTION_TIMEOUT = 5 * 60

    def doc_to_pdf(self, fio, file_path, temp_dir, config):
        """Converts an office document to PDF."""
        unoconv_bin = config['UNOCONV_BIN'] or find_executable('unoconv')
        out_file = os.path.join(temp_dir, 'out.pdf')

        unoconv = [
            unoconv_bin,
            '-f', 'pdf',
            '-o', out_file,
            file_path
        ]

        if not unoconv_bin:
            raise RuntimeError('No Libre/Open Office tools available.')

        self.logger.info('Converting %r using %r...', file_path, unoconv_bin)

        retcode = subprocess.call(unoconv, timeout=self.CONVERTION_TIMEOUT)
        assert retcode == 0, 'Execution failed: {}'.format(unoconv)
        assert os.path.exists(out_file), 'File missing: {}'.format(out_file)

        return out_file
