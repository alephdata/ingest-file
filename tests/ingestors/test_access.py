# -*- coding: utf-8 -*-
from ..support import TestCase


class AccessIngestorTest(TestCase):

    def test_simple_access(self):
        fixture_path = self.fixture('Books_be.mdb')
        result = self.manager.ingest(fixture_path)
        self.assertEqual(result.status, result.STATUS_SUCCESS)
        self.assertEqual(len(result.children), 2)
        child = result.children[0]
        self.assertEqual(child.file_name, 'authors.csv')
        self.assertEqual(child.title, 'Authors')
        self.assertEqual(len(child.rows), 3)
