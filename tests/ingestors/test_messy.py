# -*- coding: utf-8 -*-
from ..support import TestCase


class MessyTablesIngestorTest(TestCase):

    def test_simple_xlsx(self):
        fixture_path = self.fixture('file.xlsx')
        result = self.manager.ingest(fixture_path)
        self.assertEqual(result.status, result.STATUS_SUCCESS)
        self.assertEqual(len(result.children), 2)
        child = result.children[0]
        self.assertEqual(child.file_name, 'Sheet1')
        # print child.rows[0]
        self.assertEqual(child.rows[0]['Name'], 'Mihai Viteazul')

    def test_unicode_xls(self):
        fixture_path = self.fixture('rom.xls')
        result = self.manager.ingest(fixture_path)
        self.assertEqual(result.status, result.STATUS_SUCCESS)
        self.assertEqual(len(result.children), 3)
        child = result.children[0]
        self.assertEqual(child.file_name, u'Лист1')
