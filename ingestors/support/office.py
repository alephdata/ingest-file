import os.path
import logging
import subprocess32 as subprocess
from distutils.spawn import find_executable

import dateutil.parser
import messytables


class DateTimeType(messytables.types.DateUtilType):
    """Patched cell table type to offer format detection support."""

    def test(self, value):
        try:
            return dateutil.parser.parse(value)
        except Exception:
            return super(DateTimeType, self).test(value)


class OfficeSupport(object):
    """Provides helpers for Libre/Open Office tools."""

    logger = logging.getLogger(__name__)

    #: Convertion time before the job gets cancelled.
    CONVERTION_TIMEOUT = 5 * 60

    #: Table set window size
    MESSYTABLES_WINDOW = 20000
    #: Use tabular cell data format detection and auto-casting
    MESSYTABLES_TYPES_DETECTION = True

    def doc_to_pdf(self, fio, file_path, temp_dir, config):
        """Converts an office document to PDF."""
        soffice_bin = config['SOFFICE_BIN'] or find_executable('soffice')
        instance_dir = os.path.join(temp_dir, 'soffice_instance')
        out_dir = os.path.join(temp_dir, 'soffice_output')

        soffice = soffice_bin.split(' ') + [
            '-env:UserInstallation=file://{}'.format(instance_dir),
            '--nofirststartwizard',
            '--norestore',
            '--nologo',
            '--nodefault',
            '--nolockcheck',
            '--invisible',
            '--headless',
            '--convert-to', 'pdf',
            '--outdir', out_dir,
            file_path
        ]

        if not soffice_bin:
            raise RuntimeError('No Libre/Open Office tools available.')

        self.logger.info('Converting %r using %r...', file_path, soffice)

        retcode = subprocess.call(soffice, timeout=self.CONVERTION_TIMEOUT)
        assert retcode == 0, 'Execution failed: {}'.format(soffice)
        assert os.path.exists(out_dir), 'Files missing in: {}'.format(out_dir)

        for out_file in os.listdir(out_dir):
            out_file = os.path.join(out_dir, out_file)
            return out_file

        assert out_file, 'File missing: {}'.format(out_file)

    def tabular_to_tableset(self, fio, file_path, mimetype, config):
        """Parses tabular data into a set of sheets."""
        file_name, file_extension = os.path.splitext(file_path)
        tableset = messytables.any_tableset(
            fio,
            mimetype=mimetype,
            extension=file_extension,
            window=self.MESSYTABLES_WINDOW
        )

        return tableset.tables

    def sheet_row_to_dicts(self, sheet, rowset):
        """Converts a sheet rows into dictionary mappings.

        Every dictionary represents a mapping the header keys to row values.
        """
        if self.MESSYTABLES_TYPES_DETECTION:
            types_to_detect = messytables.types.TYPES[:]
            types_to_detect.remove(messytables.types.DateType)
            types_to_detect.append(DateTimeType)

            rowset.set_types(messytables.type_guess(rowset, types_to_detect))
            rowset.register_processor(
                messytables.types_processor(rowset.get_types()))

        offset, headers = messytables.headers_guess(rowset)
        rowset.register_processor(messytables.headers_processor(headers))
        rowset.register_processor(messytables.offset_processor(offset + 1))

        for mapping in rowset.dicts():
            yield mapping
