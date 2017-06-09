# -*- coding: utf-8 -*-
from pprint import pprint  # noqa

from ..support import TestCase


class OutlookPSTTest(TestCase):

    def test_match(self):
        fixture_path = self.fixture('testPST.pst')
        result = self.manager.ingest(fixture_path)
        # pprint(result.to_dict())
        self.assertEqual(result.mime_type, 'application/vnd.ms-outlook')
        self.assertEqual(len(result.children), 1)
