from __future__ import absolute_import

import unittest
import os
import types

from servicelayer.cache import get_fakeredis
from servicelayer.archive import init_archive
from servicelayer.queue import ServiceQueue
from ingestors.manager import Manager
from ingestors.util import is_file


def emit_entity(self, entity, fragment=None):
    self.entities.append(entity)
    self.writer.put(entity.to_dict(), fragment=fragment)


class TestCase(unittest.TestCase):
    queue = ServiceQueue(get_fakeredis(), ServiceQueue.OP_INGEST, 'test')
    manager = Manager(queue, {})
    manager.entities = []
    manager.emit_entity = types.MethodType(emit_entity, manager)
    archive = init_archive(archive_type='file', path='build/test/archive')

    def fixture(self, fixture_path):
        """Returns a fixture path and a dummy entity"""
        # clear out entities
        self.manager.entities = []
        self.manager.dataset.delete()
        cur_path = os.path.dirname(os.path.realpath(__file__))
        cur_path = os.path.join(cur_path, 'fixtures')
        path = os.path.join(cur_path, fixture_path)
        entity = self.manager.make_entity('Document')
        if is_file(path):
            checksum = self.archive.archive_file(path)
            entity.make_id(checksum)
            entity.set('contentHash', checksum)
            entity.set('fileSize', os.path.getsize(path))
            file_name = os.path.basename(path)
            entity.set('fileName', file_name)
        else:
            entity.make_id(fixture_path)
        return path, entity

    def get_emitted(self, schema=None):
        entities = list(self.manager.dataset.iterate())
        if schema is not None:
            entities = [e for e in entities if e.schema.is_a(schema)]
        return entities

    def get_emitted_by_id(self, id):
        return self.manager.dataset.get(id)

    def assertSuccess(self, entity):
        self.assertEqual(entity.first('processingStatus'),
                         self.manager.STATUS_SUCCESS)