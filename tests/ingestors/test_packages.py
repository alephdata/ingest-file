# -*- coding: utf-8 -*-
from pprint import pprint  # noqa

from ..support import TestCase


class PackagesTest(TestCase):

    def test_zip(self):
        fixture_path, entity = self.fixture('test-documents.zip')
        result = self.manager.ingest(fixture_path, entity)
        self.assertEqual(
            result.first('processingStatus'), self.manager.STATUS_SUCCESS
        )
        self.assertEqual(result.schema, 'Folder')

    def test_rar(self):
        fixture_path, entity = self.fixture('test-documents.rar')
        result = self.manager.ingest(fixture_path, entity)
        self.assertEqual(
            result.first('processingStatus'), self.manager.STATUS_SUCCESS
        )
        self.assertEqual(result.schema, 'Folder')

    def test_tar(self):
        fixture_path, entity = self.fixture('test-documents.tar')
        result = self.manager.ingest(fixture_path, entity)
        self.assertEqual(
            result.first('processingStatus'), self.manager.STATUS_SUCCESS
        )
        self.assertEqual(result.schema, 'Folder')
