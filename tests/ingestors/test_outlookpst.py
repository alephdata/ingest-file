# -*- coding: utf-8 -*-
from pprint import pprint  # noqa

from ..support import TestCase


class OutlookPSTTest(TestCase):

    def test_match(self):
        fixture_path = self.fixture('testPST.pst')
        result = self.manager.ingest(fixture_path)
        # pprint(result.to_dict())
        self.assertEqual(len(result.children), 1)
        self.assertIn('directory', result.flags)
