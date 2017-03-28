import unittest
import logging
from os import environ, path


class TestCase(unittest.TestCase):

    #: Flag to indicate if extra fixtures are available
    EXTRA_FIXTURES = path.exists(environ.get('EXTRA_FIXTURES_PATH') or '')

    # Enable loggin
    logging.basicConfig(level='DEBUG')

    def fixture(self, fixture_path):
        """Returns a fixture path.

        :param str fixture_path: Fixture path to check.
        :rtype: str
        """
        cur_path = path.dirname(path.realpath(__file__))
        cur_path = path.join(cur_path, 'fixtures')
        extra_path = environ.get('EXTRA_FIXTURES_PATH') or ''

        if path.exists(path.join(extra_path, fixture_path)):
            return path.join(extra_path, fixture_path)
        else:
            return path.join(cur_path, fixture_path)
