# -*- coding: utf-8 -*-
from ..support import TestCase


class DBFIngestorTest(TestCase):

    def test_simple_dbf(self):
        fixture_path = self.fixture('PAK_adm1.dbf')
        result = self.manager.ingest(fixture_path)
        self.assertEqual(result.status, result.STATUS_SUCCESS)
        self.assertEqual(len(result.rows), 8)
        row0 = result.rows[0]
        self.assertEqual(row0['name_0'], 'Pakistan')
        self.assertEqual(row0['name_1'], 'Azad Kashmir')
        self.assertIn('tabular', result.flags)
