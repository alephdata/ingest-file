# -*- coding: utf-8 -*-
from pprint import pprint  # noqa

from ..support import TestCase


class OutlookMsgTest(TestCase):

    def test_match(self):
        fixture_path, entity = self.fixture('piste.msg')
        result = self.manager.ingest(fixture_path, entity)

        self.assertEqual(result.first('title'), 'Ab auf die Piste!')
        self.assertEqual(
            result.first('processingStatus'), self.manager.STATUS_SUCCESS
        )
