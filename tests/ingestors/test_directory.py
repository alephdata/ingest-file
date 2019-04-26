# -*- coding: utf-8 -*-
from pprint import pprint  # noqa

from ..support import TestCase
from ingestors.util import make_entity


class DirectoryTest(TestCase):

    def test_normal_directory(self):
        fixture_path, entity = self.fixture('testdir')
        result = self.manager.ingest(fixture_path, entity)
        self.assertEqual(
            result.first('processingStatus'), self.manager.STATUS_SUCCESS
        )
        self.assertEqual(len(self.manager.entities), 2)
        self.assertEqual(result.schema, 'Folder')

    def test_none_directory(self):
        entity = make_entity('Document', 'test')
        result = self.manager.ingest(None, entity)
        self.assertEqual(
            result.first('processingStatus'), self.manager.STATUS_SUCCESS
        )
        self.assertEqual(len(self.manager.entities), 1)
        self.assertEqual(result.schema, 'Folder')
