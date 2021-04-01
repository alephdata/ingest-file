# -*- coding: utf-8 -*-
from pprint import pprint  # noqa

from .support import TestCase


class AppleEmlxTest(TestCase):
    def test_plaintext(self):
        fixture_path, entity = self.fixture("plaintext.emlx")
        self.manager.ingest(fixture_path, entity)
        self.assertSuccess(entity)
        pprint(entity.to_dict())
        self.assertEqual(entity.first("subject"), u"Re: Emlx library")
        self.assertIn(u"Python", entity.first("bodyText"))

    def test_richtext(self):
        fixture_path, entity = self.fixture("richtext.emlx")
        self.manager.ingest(fixture_path, entity)
        self.assertSuccess(entity)
        self.assertIn("Emlx library", entity.first("subject"))
        self.assertIn(u"Python", entity.first("bodyHtml"))
        self.assertEqual(entity.schema.name, "Email")
