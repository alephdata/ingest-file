# -*- coding: utf-8 -*-
import io
from unittest import skipUnless

from ingestors.text import TextIngestor, Ingestor

from ..support import TestCase


class TextIngestorTest(TestCase):

    def test_match(self):
        fixture_path = self.fixture('utf.txt')

        with io.open(fixture_path, mode='rb') as fio:
            ingestor_class, mime_type = Ingestor.match(fio)

        self.assertTrue(issubclass(ingestor_class, Ingestor))
        self.assertIs(ingestor_class, TextIngestor)
        self.assertEqual(mime_type, 'text/plain')

    def test_ingest_on_unicode_file(self):
        fixture_path = self.fixture('utf.txt')

        with io.open(fixture_path, mode='rb') as fio:
            ing = TextIngestor(fio, fixture_path)
            ing.run()

        self.assertEqual(ing.result.content, u'Îș unî©ođ€.')
        self.assertEqual(ing.status, TextIngestor.STATUSES.SUCCESS)
        self.assertEqual(ing.state, TextIngestor.STATES.FINISHED)

    def test_ingest_binary_mode(self):
        fixture_path = self.fixture('non_utf.txt')

        with io.open(fixture_path, mode='rb') as fio:
            ing = TextIngestor(fio, fixture_path)
            ing.run()

        self.assertEqual(ing.result.content, u'În latin1.')

    @skipUnless(TestCase.EXTRA_FIXTURES, 'No extra fixtures.')
    def test_ingest_extra_fixture(self):
        fixture_path = self.fixture('languages/udhr_ger.txt')

        with io.open(fixture_path, mode='rb') as fio:
            ing = TextIngestor(fio, fixture_path)
            ing.run()

        self.assertIsNotNone(ing.result.content)
