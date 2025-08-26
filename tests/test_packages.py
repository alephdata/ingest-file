# -*- coding: utf-8 -*-
from pprint import pprint  # noqa
from pathlib import Path

from .support import TestCase


class PackagesTest(TestCase):
    def test_zip(self):
        fixture_path, entity = self.fixture("test-documents.zip")
        self.manager.ingest(fixture_path, entity)
        self.assertEqual(entity.first("processingStatus"), self.manager.STATUS_SUCCESS)
        self.assertEqual(entity.schema.name, "Package")

    def test_zip_symlink_escape(self):
        fixture_path, entity = self.fixture("badzip.zip")

        # Ensure that the symlink target exists
        target = Path("/ingestors/tests/fixtures/secret.txt")
        assert target.read_text() == "This is a secret!"

        self.manager.ingest(fixture_path, entity)

        # Python’s zipfile handles symlinks that point to files outside of the archive root
        # treating them as normal files
        assert len(self.manager.entities) == 2
        assert self.manager.entities[0].first("fileName") == "secret.txt"
        assert (
            self.manager.entities[0].first("bodyText")
            == "/ingestors/tests/fixtures/secret.txt"
        )
        assert self.manager.entities[1].first("fileName") == "badzip.zip"

    def test_rar(self):
        fixture_path, entity = self.fixture("test-documents.rar")
        self.manager.ingest(fixture_path, entity)
        self.assertEqual(entity.first("processingStatus"), self.manager.STATUS_SUCCESS)
        self.assertEqual(entity.schema.name, "Package")

    def test_rar_symlink_escape(self):
        fixture_path, entity = self.fixture("badrar.rar")

        # Ensure that the symlink target exists
        target = Path("/ingestors/tests/fixtures/secret.txt")
        assert target.read_text() == "This is a secret!"

        self.manager.ingest(fixture_path, entity)

        # rarfile handles symlinks that point to files outside of the archive root
        # treating them as normal files
        assert len(self.manager.entities) == 2
        assert self.manager.entities[0].first("fileName") == "secret.txt"
        assert (
            self.manager.entities[0].first("bodyText")
            == "/ingestors/tests/fixtures/secret.txt"
        )
        assert self.manager.entities[1].first("fileName") == "badrar.rar"

    def test_tar(self):
        fixture_path, entity = self.fixture("test-documents.tar")
        self.manager.ingest(fixture_path, entity)
        self.assertEqual(entity.first("processingStatus"), self.manager.STATUS_SUCCESS)
        self.assertEqual(entity.schema.name, "Package")

    def test_tar_symlink_escape(self):
        fixture_path, entity = self.fixture("badtar.tar")

        # Ensure that the symlink target exists
        target = Path("/ingestors/tests/fixtures/secret.txt")
        assert target.read_text() == "This is a secret!"

        self.manager.ingest(fixture_path, entity)

        # Python’s tarfile ignores symlinks that point to files outside of the archive root
        assert len(self.manager.entities) == 1
        assert self.manager.entities[0].first("fileName") == "badtar.tar"

    def test_7zip_symlink_escape(self):
        fixture_path, entity = self.fixture("bad7zip.7z")

        # Ensure that the symlink target exists
        target = Path("/ingestors/tests/fixtures/secret.txt")
        assert target.read_text() == "This is a secret!"

        self.manager.ingest(fixture_path, entity)

        # py7zr raises an exception if it encounters a symlink that points to a file
        # outside of the archive root
        assert len(self.manager.entities) == 1
        assert self.manager.entities[0].first("fileName") == "bad7zip.7z"
        assert self.manager.entities[0].first("processingStatus") == "failure"

    def test_7zip_password(self):
        fixture_path, entity = self.fixture("7z_password.7z")

        self.manager.ingest(fixture_path, entity)

        assert len(self.manager.entities) == 1
        assert self.manager.entities[0].first("fileName") == "7z_password.7z"
        assert self.manager.entities[0].first("processingStatus") == "failure"
