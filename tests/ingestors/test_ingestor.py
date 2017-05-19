import io
from datetime import datetime

from ingestors.ingestor import Ingestor

from ..support import TestCase


class MyIngestor(Ingestor):

    def configure(self):
        return {'configured': True}

    def before(self):
        self.result.before = True

    def after(self):
        self.result.after = True

    def ingest(self, config):
        self.result.update(config)
        self.result.content = str(self.fio)


class MyFailedIngestor(MyIngestor):

    def ingest(self, config):
        exception_class = Ingestor.FAILURE_EXCEPTIONS[0]
        raise exception_class()


class MyStoppedIngestor(MyIngestor):

    def ingest(self, config):
        raise IOError()


class IngestorTest(TestCase):

    def test_ingest_success(self):
        fio = io.BytesIO(b'')
        ing = MyIngestor(fio, file_path='myfile.txt')

        self.assertEqual(ing.status, Ingestor.STATUSES.SUCCESS)
        self.assertEqual(ing.state, Ingestor.STATES.NEW)
        self.assertIsInstance(ing.result, Ingestor.RESULT_CLASS)
        self.assertIsNone(ing.started_at)
        self.assertIsNone(ing.ended_at)

        ing.run()

        self.assertIsInstance(ing.started_at, datetime)
        self.assertIsInstance(ing.ended_at, datetime)
        self.assertEqual(ing.status, Ingestor.STATUSES.SUCCESS)
        self.assertEqual(ing.state, Ingestor.STATES.FINISHED)
        self.assertDictContainsSubset(
            {
                'content': str(fio),
                'before': True,
                'after': True,
                'configured': True
            },
            ing.result
        )

    def test_ingest_stopped(self):
        fio = io.BytesIO(b'')
        ing = MyStoppedIngestor(fio, file_path='myfile.txt')

        self.assertEqual(ing.status, Ingestor.STATUSES.SUCCESS)
        self.assertEqual(ing.state, Ingestor.STATES.NEW)

        ing.run()

        self.assertIsInstance(ing.started_at, datetime)
        self.assertIsInstance(ing.ended_at, datetime)
        self.assertEqual(ing.status, Ingestor.STATUSES.STOPPED)
        self.assertEqual(ing.state, Ingestor.STATES.FINISHED)
        self.assertDictContainsSubset(
            {'before': True, 'after': True}, ing.result
        )

    def test_ingest_failure(self):
        fio = io.BytesIO(b'')
        ing = MyFailedIngestor(fio, file_path='myfile.txt')

        self.assertEqual(ing.status, Ingestor.STATUSES.SUCCESS)
        self.assertEqual(ing.state, Ingestor.STATES.NEW)

        ing.run()

        self.assertIsInstance(ing.started_at, datetime)
        self.assertIsInstance(ing.ended_at, datetime)
        self.assertEqual(ing.status, Ingestor.STATUSES.FAILURE)
        self.assertEqual(ing.state, Ingestor.STATES.FINISHED)
        self.assertDictContainsSubset(
            {'before': True, 'after': True}, ing.result
        )

    def test_find_ingestors(self):
        ingestors = Ingestor.find_ingestors()

        self.assertEqual(len(ingestors), 6)

        for ingestor_class in ingestors:
            self.assertTrue(issubclass(ingestor_class, Ingestor))
