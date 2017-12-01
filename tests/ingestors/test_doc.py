# -*- coding: utf-8 -*-
from datetime import datetime

from ..support import TestCase


class DocumentIngestorTest(TestCase):

    def test_match(self):
        fixture_path = self.fixture('hello world word.docx')
        result = self.manager.ingest(fixture_path)
        self.assertEqual(
            result.mime_type,
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'  # noqa
        )

    def test_ingest_word_doc(self):
        fixture_path = self.fixture('doc.doc')
        result = self.manager.ingest(fixture_path)

        self.assertEqual(len(result.pages), 2)
        self.assertIn(
            u'This is a sample Microsoft Word Document.',
            result.pages[0]['text']
        )

        self.assertIn(
            u'The Level 3 Bookmark',
            result.pages[1]['text']
        )
        self.assertIn('pdf', result.flags)

    def test_ingest_presentation_doc(self):
        fixture_path = self.fixture('slides.ppt')
        result = self.manager.ingest(fixture_path)

        today = datetime.now()

        self.assertEqual(len(result.pages), 1)
        self.assertIn(u'Now', result.pages[0]['text'])
        self.assertIn('pdf', result.flags)
        self.assertIn(
            today.strftime('%x'),
            result.pages[0]['text']
        )

    def test_ingest_encrypted_doc(self):
        fixture_path = self.fixture('encypted_by_libreoffice.odt')
        result = self.manager.ingest(fixture_path)

        self.assertEqual(result.status, result.STATUS_FAILURE)

    def test_ingest_noisy_doc(self):
        fixture_path = self.fixture('Plan.odt')
        result = self.manager.ingest(fixture_path)
        # print result.to_dict()
        self.assertEqual(len(result.pages), 1)
        self.assertIn(
            'We should paint graffiti on all corners',
            result.pages[0]['text']
        )

    def test_ingest_virus_macros_doc(self):
        fixture_path = self.fixture('INV-IN174074-2016-386.doc')
        result = self.manager.ingest(fixture_path)

        self.assertEqual(len(result.pages), 1)
