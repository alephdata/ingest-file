# -*- coding: utf-8 -*-
import io
from unittest import skipUnless

from ingestors.doc import DocumentIngestor

from ..support import TestCase


class DocumentIngestorTest(TestCase):

    def test_ingest_on_unicode_file(self):
        fixture_path = self.fixture('doc.doc')

        with io.open(fixture_path, mode='rb') as fio:
            ing = DocumentIngestor(fio, fixture_path)
            ing.run()

        self.assertIsNone(ing.result.content)
        self.assertEqual(len(ing.children), 2)
        self.assertIn(
            u'This is a sample Microsoft Word Document.',
            ing.children[0].result.content
        )
        self.assertIn(
            u'This one is in a different one, the Signature style',
            ing.children[1].result.content
        )

    @skipUnless(TestCase.EXTRA_FIXTURES, 'No extra fixtures.')
    def test_ingest_encrypted_doc(self):
        fixture_path = self.fixture('bad/encypted_by_libreoffice.docx')

        with io.open(fixture_path, mode='rb') as fio:
            ing = DocumentIngestor(fio, fixture_path)
            ing.run()

        self.assertIsNone(ing.result.content)

        # TODO: This file should fail because it requires a password.
        # Consider using alternative tools for handling the converstion
        # See: https://github.com/dagwieers/unoconv
        self.assertEqual(len(ing.children), 17)

    @skipUnless(TestCase.EXTRA_FIXTURES, 'No extra fixtures.')
    def test_ingest_bad_doc(self):
        fixture_path = self.fixture('bad/REALLY_NOT_DOCX_BUT_BINARY_DATA.docx')

        with io.open(fixture_path, mode='rb') as fio:
            ing = DocumentIngestor(fio, fixture_path)
            ing.run()

        self.assertIsNone(ing.result.content)
        # TODO: This file should fail because it is just binary garbage.
        self.assertEqual(len(ing.children), 117)

    @skipUnless(TestCase.EXTRA_FIXTURES, 'No extra fixtures.')
    def test_ingest_noisy_doc(self):
        fixture_path = self.fixture(
            'investigators/Case1/Smith from Dzmitry Lahoda phone/Plan.odt'
        )

        with io.open(fixture_path, mode='rb') as fio:
            ing = DocumentIngestor(fio, fixture_path)
            ing.run()

        self.assertIsNone(ing.result.content)
        self.assertEqual(len(ing.children), 1)
        self.assertIn(
            'We should paint graffiti on all corners',
            ing.children[0].result.content
        )

    @skipUnless(TestCase.EXTRA_FIXTURES, 'No extra fixtures.')
    def test_ingest_virus_macros_doc(self):
        fixture_path = self.fixture(
            'virus/INV-IN174074-2016-386.doc'
        )

        with io.open(fixture_path, mode='rb') as fio:
            ing = DocumentIngestor(fio, fixture_path)
            ing.run()

        self.assertIsNone(ing.result.content)
        self.assertEqual(len(ing.children), 1)
        self.assertIsNone(ing.children[0].result.content)

    @skipUnless(TestCase.EXTRA_FIXTURES, 'No extra fixtures.')
    def test_ingest_doc_with_images(self):
        fixture_path = self.fixture(
            'virus/word document with 42 zip.docx'
        )

        with io.open(fixture_path, mode='rb') as fio:
            ing = DocumentIngestor(fio, fixture_path)
            ing.run()

        self.assertIsNone(ing.result.content)
        self.assertEqual(len(ing.children), 1)
        self.assertEqual(
            u'b\nJ\n\n42. zip 42. zip.txt',
            ing.children[0].result.content
        )
