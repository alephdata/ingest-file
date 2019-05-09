# -*- coding: utf-8 -*-
from ..support import TestCase


class TabularIngestorTest(TestCase):

    def test_simple_xlsx(self):
        fixture_path, entity = self.fixture('file.xlsx')
        self.manager.ingest(fixture_path, entity)
        self.assertEqual(
            entity.first('processingStatus'), self.manager.STATUS_SUCCESS
        )
        row1 = self.manager.entities[1]
        self.assertEqual(row1.schema, 'Row')
        self.assertIn('Mihai Viteazul', row1.get('cells'))
        row0 = self.manager.entities[0]
        self.assertIn('Name', row0.get('cells'))
        sheet1 = self.manager.entities[3]
        self.assertEqual(sheet1.schema, 'Table')
        self.assertEqual(sheet1.first('title'), 'Sheet1')
        self.assertEqual(entity.schema, 'Workbook')

    def test_unicode_xls(self):
        fixture_path, entity = self.fixture('rom.xls')
        self.manager.ingest(fixture_path, entity)
        self.assertEqual(
            entity.first('processingStatus'), self.manager.STATUS_SUCCESS
        )
        self.assertEqual(entity.schema, 'Workbook')
        sheet1 = next((x for x in self.manager.entities if x.schema == 'Table'), None)  # noqa
        self.assertEqual(sheet1.first('title'), u'Лист1')

    def test_unicode_ods(self):
        fixture_path, entity = self.fixture('rom.ods')
        self.manager.ingest(fixture_path, entity)
        self.assertEqual(
            entity.first('processingStatus'), self.manager.STATUS_SUCCESS
        )
        sheet1 = next((x for x in self.manager.entities if x.schema == 'Table'), None)  # noqa
        self.assertEqual(sheet1.first('title'), u'Лист1')
        self.assertEqual(entity.schema, 'Workbook')
