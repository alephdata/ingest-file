# -*- coding: utf-8 -*-
from ..support import TestCase


class DBFIngestorTest(TestCase):

    def test_simple_dbf(self):
        fixture_path, entity = self.fixture('PAK_adm1.dbf')
        self.manager.ingest(fixture_path, entity)
        self.assertEqual(
            entity.first('processingStatus'), self.manager.STATUS_SUCCESS
        )
        # 8 rows + 1 table
        self.assertEqual(len(self.manager.entities), 8+1)
        self.assertEqual(entity.schema, 'Table')
        row0 = self.manager.entities[0]
        self.assertIn('Azad Kashmir', row0.get('cells'))
        self.assertIn('Pakistan', row0.get('cells'))
