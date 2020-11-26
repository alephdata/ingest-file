# -*- coding: utf-8 -*-

from .support import TestCase


class CalendarIngestorTest(TestCase):
    def test_match(self):
        fixture_path, entity = self.fixture("meetup.ics")
        self.manager.ingest(fixture_path, entity)
        entities = self.get_emitted()
        assert len(entities) == 5, entities
        schemata = [e.schema.name for e in entities]
        assert "Person" in schemata, entities
        assert "Event" in schemata, entities
        assert "PlainText" in schemata, entities
