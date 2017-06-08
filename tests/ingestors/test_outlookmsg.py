# -*- coding: utf-8 -*-
from pprint import pprint  # noqa

from ..support import TestCase


class OutlookMsgTest(TestCase):

    def test_match(self):
        fixture_path = self.fixture('piste.msg')
        result = self.manager.ingest(fixture_path)

        self.assertEqual(result.title, 'Ab auf die Piste!')
        self.assertEqual(result.status, result.STATUS_SUCCESS)
