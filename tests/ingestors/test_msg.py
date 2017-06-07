# -*- coding: utf-8 -*-
from pprint import pprint  # noqa

from ..support import TestCase


class RFC822Test(TestCase):

    def test_match(self):
        fixture_path = self.fixture('testThunderbirdEml.eml')
        result = self.manager.ingest(fixture_path)
        pprint(result.to_dict())
        self.assertEqual(result.status, result.STATUS_SUCCESS)
        self.assertEqual(result.title, u'JUnit test message')
        self.assertIn(u'Dear Vladimir', result.pages[0]['text'])
