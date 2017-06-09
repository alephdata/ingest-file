from __future__ import absolute_import

import unittest
from os import path

from ingestors import Manager


class TestCase(unittest.TestCase):

    manager = Manager({})

    def fixture(self, fixture_path):
        """Returns a fixture path.

        :param str fixture_path: Fixture path to check.
        :rtype: str
        """
        cur_path = path.dirname(path.realpath(__file__))
        cur_path = path.join(cur_path, 'fixtures')
        return path.join(cur_path, fixture_path)
