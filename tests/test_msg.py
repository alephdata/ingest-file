# -*- coding: utf-8 -*-
from pprint import pprint  # noqa

from .support import TestCase


class RFC822Test(TestCase):
    def test_thunderbird(self):
        fixture_path, entity = self.fixture("testThunderbirdEml.eml")
        self.manager.ingest(fixture_path, entity)
        self.assertSuccess(entity)
        pprint(entity.to_dict())
        self.assertEqual(entity.first("subject"), "JUnit test message")
        self.assertIn("Dear Vladimir", entity.first("bodyText"))

    def test_naumann(self):
        fixture_path, entity = self.fixture("fnf.msg")
        self.manager.ingest(fixture_path, entity)
        self.assertSuccess(entity)
        self.assertIn("Innovationskongress", entity.first("subject"))
        self.assertIn("freiheit.org", entity.first("bodyHtml"))
        self.assertEqual(entity.schema.name, "Email")

    def test_mbox(self):
        fixture_path, entity = self.fixture("plan.mbox")
        self.manager.ingest(fixture_path, entity)
        self.assertSuccess(entity)
        self.assertEqual(entity.schema.name, "Package")
