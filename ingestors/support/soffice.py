import os
import logging

from ingestors.support.pdf import PDFSupport
from ingestors.support.uno import UnoconvSupport
from ingestors.exc import ProcessingException
from ingestors.util import join_path, make_directory

log = logging.getLogger(__name__)


class LibreOfficeSupport(PDFSupport, UnoconvSupport):
    """Provides helpers for Libre/Open Office tools."""

    def document_to_pdf(self, file_path):
        """Converts an office document to PDF."""
        if self.is_unoconv_available():
            return self.unoconv_to_pdf(file_path)

        instance_dir = make_directory(self.work_path, 'soffice_instance')
        out_dir = make_directory(self.work_path, 'soffice_output')
        log.info('Converting [%s] to PDF...', file_path)
        instance_dir = '-env:UserInstallation=file://{}'.format(instance_dir)
        self.exec_command('soffice',
                          instance_dir,
                          '--nofirststartwizard',
                          '--norestore',
                          '--nologo',
                          '--nodefault',
                          '--nolockcheck',
                          '--invisible',
                          '--headless',
                          '--convert-to', 'pdf',
                          '--outdir', out_dir,
                          file_path)

        for out_file in os.listdir(out_dir):
            return join_path(out_dir, out_file)

        msg = "Failed to convert to PDF: {}".format(file_path)
        raise ProcessingException(msg)
