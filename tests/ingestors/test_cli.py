# -*- coding: utf-8 -*-
from ..support import TestCase


class CliTest(TestCase):

    def test_cli_single(self):
        fixture_path = self.fixture('utf.txt')
        result = self.manager.ingest(fixture_path)

        self.assertEqual(result.size, 19)
        self.assertEqual(result.mime_type, 'text/plain')
        self.assertEqual(result.checksum,
                         '5a6acf229ba576d9a40b09292595658bbb74ef56')
