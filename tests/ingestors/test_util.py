# -*- coding: utf-8 -*-
from ..support import TestCase
from ingestors.util import normalize_extension


class UtilTest(TestCase):

    def test_normalize_extension(self):
        self.assertEqual(normalize_extension('TXT'), 'txt')
        self.assertEqual(normalize_extension('.TXT'), 'txt')
        self.assertEqual(normalize_extension('foo.txt'), 'txt')
        self.assertEqual(normalize_extension('foo..TXT'), 'txt')
        self.assertEqual(normalize_extension('.HTM,L'), 'html')
