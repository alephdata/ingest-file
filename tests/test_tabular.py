# -*- coding: utf-8 -*-
from .support import TestCase
from ingestors.exc import ENCRYPTED_MSG


class TabularIngestorTest(TestCase):
    def test_simple_xlsx(self):
        fixture_path, entity = self.fixture("file.xlsx")
        self.manager.ingest(fixture_path, entity)
        self.assertEqual(entity.first("processingStatus"), self.manager.STATUS_SUCCESS)
        self.assertEqual(entity.schema.name, "Workbook")
        tables = self.get_emitted("Table")
        self.assertEqual(len(tables), 2)
        titles = [t.first("title") for t in tables]
        self.assertIn("Sheet1", titles)
        table = [t for t in tables if "1" in t.first("title")][0]
        self.assertTrue(table.has("csvHash"))
        self.assertEqual(int(table.first("rowCount")), 3)
        self.assertIn("Mihai Viteazul", table.get("indexText"))

    def test_unicode_xls(self):
        fixture_path, entity = self.fixture("rom.xls")
        self.manager.ingest(fixture_path, entity)
        self.assertEqual(entity.first("processingStatus"), self.manager.STATUS_SUCCESS)
        self.assertEqual(entity.schema.name, "Workbook")
        tables = self.get_emitted("Table")
        tables = [t.first("title") for t in tables]
        self.assertIn("Лист1", tables)

    def test_unicode_ods(self):
        fixture_path, entity = self.fixture("rom.ods")
        self.manager.ingest(fixture_path, entity)
        self.assertEqual(entity.first("processingStatus"), self.manager.STATUS_SUCCESS)
        tables = self.get_emitted("Table")
        tables = [t.first("title") for t in tables]
        self.assertIn("Лист1", tables)
        self.assertEqual(entity.schema.name, "Workbook")

    def test_password_protected_xlsx(self):
        fixture_path, entity = self.fixture("password_protected.xlsx")
        self.manager.ingest(fixture_path, entity)
        self.assertEqual(len(self.get_emitted()), 1)
        err = self.manager.entities[0].first("processingError")
        self.assertIn(ENCRYPTED_MSG, err)
        status = self.manager.entities[0].first("processingStatus")
        self.assertEqual("failure", status)

    def test_password_protected_xls(self):
        fixture_path, entity = self.fixture("password_protected.xls")
        self.manager.ingest(fixture_path, entity)
        self.assertEqual(len(self.get_emitted()), 1)
        err = self.manager.entities[0].first("processingError")
        self.assertIn(ENCRYPTED_MSG, err)
        status = self.manager.entities[0].first("processingStatus")
        self.assertEqual("failure", status)

    def test_metadata_inheritance(self):
        fixture_path, entity = self.fixture("staff_list.xlsx")
        self.manager.ingest(fixture_path, entity)
        table_entities = self.get_emitted("Table")
        import pprint

        pprint.pprint([x.to_dict() for x in table_entities])
        parent_entity = self.get_emitted("Workbook").pop()
        self.assertEqual(len(table_entities), 3)

        for metadatum in [
            "authoredAt",
            "modifiedAt",
            "author",
            "summary",
            "generator",
            "language",
            "processingAgent",
        ]:
            for table_entity in table_entities:
                self.assertEqual(
                    table_entity.get(metadatum), parent_entity.get(metadatum)
                )
