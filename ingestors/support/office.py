import os.path
import subprocess32 as subprocess
from distutils.spawn import find_executable


class OfficeSupport(object):
    """Provides helpers for Libre/Open Office tools."""

    #: Convertion time before the job gets cancelled.
    CONVERTION_TIMEOUT = 5 * 60

    def doc_to_pdf(self, fio, file_path, temp_dir, config):
        soffice_bin = config['SOFFICE_BIN'] or find_executable('soffice')
        work_dir = os.path.join(temp_dir, 'work_dir')
        inst_dir = os.path.join(temp_dir, 'inst_dir')
        inst_path = u'"-env:UserInstallation=file://{}"'.format(inst_dir)

        soffice = [
            soffice_bin,
            '--convert-to', 'pdf',
            '--nofirststartwizard',
            inst_path,
            '--norestore',
            '--nologo',
            '--nodefault',
            '--nolockcheck',
            '--invisible',
            '--outdir', work_dir,
            '--headless',
            file_path
        ]

        if not soffice_bin:
            raise RuntimeError('No Libre/Open Office tools available.')

        self.logger.info('Converting %r using %r...', file_path, soffice_bin)

        retcode = subprocess.call(soffice, timeout=self.CONVERTION_TIMEOUT)
        conv_files = os.listdir(work_dir)
        assert retcode == 0, 'Execution failed: %r'.format(soffice)
        assert len(conv_files) == 1, 'Unexpected files: %r'.format(work_dir)

        for out_file in conv_files:
            yield os.path.join(work_dir, out_file)
