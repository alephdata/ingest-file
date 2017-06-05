import os
import logging

from ingestors.support.pdf import PDFSupport
from ingestors.exc import ProcessingException

log = logging.getLogger(__name__)


class LibreOfficeSupport(PDFSupport):
    """Provides helpers for Libre/Open Office tools."""

    def document_to_pdf(self, file_path, temp_dir):
        """Converts an office document to PDF."""
        instance_dir = os.path.join(temp_dir, 'soffice_instance')
        out_dir = os.path.join(temp_dir, 'soffice_output')
        try:
            os.makedirs(out_dir)
        except:
            pass
        log.info('Converting %r to PDF...', file_path)
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
            out_file = os.path.join(out_dir, out_file)
            return out_file

        msg = "Failed to convert to PDF: {}".format(file_path)
        raise ProcessingException(msg)
