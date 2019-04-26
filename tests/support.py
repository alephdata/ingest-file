from __future__ import absolute_import

import unittest
import os
import types

from servicelayer.archive import init_archive
from ingestors import Manager
from ingestors.util import make_entity, is_file


def emit_entity(self, entity):
    self.entities.append(entity)
    return entity


class TestCase(unittest.TestCase):

    manager = Manager('test', {})
    manager.entities = []
    manager.emit_entity = types.MethodType(emit_entity, manager)
    archive = init_archive(archive_type='file', path='build/test/archive')

    def fixture(self, fixture_path):
        """Returns a fixture path and a dummy entity"""
        self.manager.entities = []
        cur_path = os.path.dirname(os.path.realpath(__file__))
        cur_path = os.path.join(cur_path, 'fixtures')
        path = os.path.join(cur_path, fixture_path)
        entity = make_entity('Document', 'test')
        if is_file(path):
            checksum = self.archive.archive_file(path)
            entity.id = checksum
            entity.set('contentHash', checksum)
            entity.set('fileSize', os.path.getsize(path))
            file_name = os.path.basename(path)
            entity.set('fileName', file_name)
        return path, entity
