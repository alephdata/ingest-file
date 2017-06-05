import os
import six
import logging
if six.PY2:
    import subprocess32 as subprocess
else:
    import subprocess
from distutils.spawn import find_executable

from ingestors.exc import SystemException, ProcessingException

log = logging.getLogger(__name__)


class ShellSupport(object):
    """Provides helpers for shell commands."""

    #: Convertion time before the job gets cancelled.
    COMMAND_TIMEOUT = 10 * 60

    subprocess = subprocess

    def find_command(self, name):
        config_name = '%s_bin' % name
        config_name = config_name.upper()
        command_path = self.manager.get_env(config_name, find_executable(name))
        if command_path is None:
            raise SystemException('Cannot find binary: %s' % name)
        return command_path

    def exec_command(self, command, *args):
        cmd = [self.find_command(command)]
        cmd.extend(args)
        retcode = subprocess.call(cmd, timeout=self.COMMAND_TIMEOUT,
                                  stdout=open(os.devnull, 'wb'))
        if retcode != 0:
            raise ProcessingException('Failed: %s' % ' '.join(cmd))

    def assert_outfile(self, path):
        if not os.path.exists(path):
            raise ProcessingException('File missing: {}'.format(path))
