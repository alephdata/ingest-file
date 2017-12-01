# -*- coding: utf-8 -*-
from pprint import pprint  # noqa

from ..support import TestCase


class PackagesTest(TestCase):

    def test_zip(self):
        fixture_path = self.fixture('test-documents.zip')
        result = self.manager.ingest(fixture_path)
        self.assertEqual(result.status, result.STATUS_SUCCESS)
        self.assertEqual(len(result.children), 9)
        self.assertIn('package', result.flags)

    def test_rar(self):
        fixture_path = self.fixture('test-documents.rar')
        result = self.manager.ingest(fixture_path)
        self.assertEqual(result.status, result.STATUS_SUCCESS)
        self.assertEqual(len(result.children), 1)
        self.assertIn('package', result.flags)

    def test_tar(self):
        fixture_path = self.fixture('test-documents.tar')
        result = self.manager.ingest(fixture_path)
        self.assertEqual(result.status, result.STATUS_SUCCESS)
        self.assertEqual(len(result.children), 1)
        self.assertIn('package', result.flags)
