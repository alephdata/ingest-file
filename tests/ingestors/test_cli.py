# -*- coding: utf-8 -*-
from ingestors import cli

from ..support import TestCase


class CliTest(TestCase):

    def test_cli_single(self):
        fixture_path = self.fixture('utf.txt')

        data = cli.cli(fixture_path, echo=False)

        self.assertEqual(data, {
            'title': 'utf.txt',
            'checksum': '5a6acf229ba576d9a40b09292595658bbb74ef56',
            'file_size': 19,
            'content': u'Îș unî©ođ€.',
            'authors': [],
            'order': 0,
            'mime_type': 'text/plain'
        })

    def test_cli_children(self):
        fixture_path = self.fixture('readme.pdf')

        data = cli.cli(fixture_path, echo=False)
        children = data.pop('children')

        self.assertEqual(data, {
            'title': 'readme.pdf',
            'checksum': 'f26b980762285ab31143792df9b8d1dfa9643cb0',
            'file_size': 73627,
            'content': None,
            'authors': [],
            'order': 0,
            'mime_type': 'application/pdf'
        })

        self.assertIsNotNone(children[0].pop('content'))

        self.assertEqual(children[0], {
            'news_keywords': None,
            'keywords': None,
            'description': None,
            'urls': {},
            'title': None,
            'checksum': None,
            'file_size': 0,
            'authors': [],
            'order': 1,
            'mime_type': None
        })
