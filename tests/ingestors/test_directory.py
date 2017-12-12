# -*- coding: utf-8 -*-
from pprint import pprint  # noqa

from ..support import TestCase


class DirectoryTest(TestCase):

    def test_normal_directory(self):
        fixture_path = self.fixture('testdir')
        result = self.manager.ingest(fixture_path)
        self.assertEqual(result.status, result.STATUS_SUCCESS)
        self.assertEqual(len(result.children), 1)
        self.assertIn('directory', result.flags)

    def test_none_directory(self):
        result = self.manager.ingest(None)
        self.assertEqual(result.status, result.STATUS_SUCCESS)
        self.assertEqual(len(result.children), 0)
        self.assertIn('directory', result.flags)
