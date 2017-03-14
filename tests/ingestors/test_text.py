# -*- coding: utf-8 -*-
import io
from unittest import skipUnless

from ingestors.text import TextIngestor

from ..support import TestCase


class TextIngestorTest(TestCase):

    def test_ingest_forces_utf8(self):
        fixture_path = self.fixture('non_utf.txt')

        with io.open(fixture_path, encoding='utf-8') as fio:
            ing = TextIngestor(fio, fixture_path)
            ing.run()

        self.assertIsNone(ing.body)
        self.assertEqual(ing.status, TextIngestor.STATUSES.FAILURE)
        self.assertEqual(ing.state, TextIngestor.STATES.FINISHED)

    def test_ingest_on_unicode_file(self):
        fixture_path = self.fixture('utf.txt')

        with io.open(fixture_path, mode='rb') as fio:
            ing = TextIngestor(fio, fixture_path)
            ing.run()

        self.assertEqual(ing.body.strip(), u'Îș unî©ođ€.')
        self.assertEqual(ing.status, TextIngestor.STATUSES.SUCCESS)
        self.assertEqual(ing.state, TextIngestor.STATES.FINISHED)

    def test_ingest_binary_mode(self):
        fixture_path = self.fixture('non_utf.txt')

        with io.open(fixture_path, mode='rb') as fio:
            ing = TextIngestor(fio, fixture_path)
            ing.run()

        self.assertEqual(ing.body.strip(), u'În latin1.')
        self.assertEqual(ing.status, TextIngestor.STATUSES.SUCCESS)
        self.assertEqual(ing.state, TextIngestor.STATES.FINISHED)

    @skipUnless(TestCase.EXTRA_FIXTURES, 'No extra fixtures.')
    def test_ingest_extra_fixture(self):
        fixture_path = self.fixture('languages/udhr_ger.txt')

        with io.open(fixture_path, mode='rb') as fio:
            ing = TextIngestor(fio, fixture_path)
            ing.run()

        self.assertIsNotNone(ing.body)
        self.assertEqual(ing.status, TextIngestor.STATUSES.SUCCESS)
        self.assertEqual(ing.state, TextIngestor.STATES.FINISHED)
