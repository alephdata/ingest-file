# -*- coding: utf-8 -*-
from pprint import pprint  # noqa

from ..support import TestCase


class RFC822Test(TestCase):

    def test_thunderbird(self):
        fixture_path = self.fixture('testThunderbirdEml.eml')
        result = self.manager.ingest(fixture_path)
        # pprint(result.to_dict())
        self.assertEqual(result.status, result.STATUS_SUCCESS)
        self.assertEqual(result.title, u'JUnit test message')
        self.assertIn(u'Dear Vladimir', result.pages[0]['text'])

    def test_naumann(self):
        fixture_path = self.fixture('fnf.msg')
        result = self.manager.ingest(fixture_path)
        # pprint(result.to_dict())
        self.assertEqual(result.status, result.STATUS_SUCCESS)
        self.assertIn('Innovationskongress', result.title)
        self.assertIn(u'freiheit.org', result.pages[0]['text'])

    def test_mbox(self):
        fixture_path = self.fixture('plan.mbox')
        result = self.manager.ingest(fixture_path)
        # pprint(result.to_dict())
        self.assertEqual(result.status, result.STATUS_SUCCESS)
