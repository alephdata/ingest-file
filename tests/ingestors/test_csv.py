# -*- coding: utf-8 -*-
from ..support import TestCase


class CSVIngestorTest(TestCase):

    def test_simple_csv(self):
        fixture_path = self.fixture('countries.csv')
        result = self.manager.ingest(fixture_path)
        self.assertEqual(result.status, result.STATUS_SUCCESS)
        self.assertEqual(len(result.rows), 256)
        self.assertIn('tabular', result.flags)

    def test_nonutf_csv(self):
        fixture_path = self.fixture('countries_nonutf.csv')
        result = self.manager.ingest(fixture_path)
        self.assertEqual(result.status, result.STATUS_SUCCESS)
        self.assertEqual(len(result.rows), 20)
        self.assertIn('tabular', result.flags)
        self.assertNotIn('workbook', result.flags)
