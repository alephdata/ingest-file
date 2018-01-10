import os
import six
import logging
from distutils.spawn import find_executable
from ingestors.exc import SystemException, ProcessingException

if six.PY2:
    import subprocess32 as subprocess  # noqa
else:
    import subprocess  # noqa

log = logging.getLogger(__name__)


class ShellSupport(object):
    """Provides helpers for shell commands."""

    #: Convertion time before the job gets cancelled.
    COMMAND_TIMEOUT = 10 * 60

    subprocess = subprocess

    def find_command(self, name):
        config_name = '%s_bin' % name
        config_name = config_name.replace('-', '_').upper()
        command_path = self.manager.get_env(config_name, find_executable(name))
        if command_path is None:
            raise SystemException('Cannot find binary: %s' % name)
        return command_path

    def exec_command(self, command, *args):
        cmd = [self.find_command(command)]
        cmd.extend(args)

        try:
            retcode = subprocess.call(cmd, timeout=self.COMMAND_TIMEOUT,
                                      stdout=open(os.devnull, 'wb'))
        except (IOError, OSError) as ose:
            raise ProcessingException('Error: %s' % ose)
        except subprocess.TimeoutExpired:
            raise ProcessingException('Processing timed out.')

        if retcode != 0:
            raise ProcessingException('Failed: %s' % ' '.join(cmd))

    def assert_outfile(self, path):
        if not os.path.exists(path):
            raise ProcessingException('File missing: {}'.format(path))
