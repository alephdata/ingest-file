# -*- coding: utf-8 -*-
from ..support import TestCase


class CSVIngestorTest(TestCase):

    def test_simple_csv(self):
        fixture_path, entity = self.fixture('countries.csv')
        result = self.manager.ingest(fixture_path, entity)
        self.assertEqual(
            result.first('processingStatus'), self.manager.STATUS_SUCCESS
        )
        # 256 rows + 1 table
        self.assertEqual(len(self.manager.entities), 256+1)
        self.assertEqual(result.schema, 'Table')

    def test_nonutf_csv(self):
        fixture_path, entity = self.fixture('countries_nonutf.csv')
        result = self.manager.ingest(fixture_path, entity)
        self.assertEqual(
            result.first('processingStatus'), self.manager.STATUS_SUCCESS
        )
        # 20 rows + 1 table
        self.assertEqual(len(self.manager.entities), 20+1)
        self.assertEqual(result.schema, 'Table')
