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
        fio = {'fake_file_io': True}
        ing = MyIngestor(fio, file_path='myfile.txt')

        self.assertEqual(ing.status, Ingestor.STATUSES.SUCCESS)
        self.assertEqual(ing.state, Ingestor.STATES.NEW)
        self.assertIsInstance(ing.result, Ingestor.RESULT_CLASS)

        ing.run()

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
        fio = {'fake_file_io': True}
        ing = MyStoppedIngestor(fio, file_path='myfile.txt')

        self.assertEqual(ing.status, Ingestor.STATUSES.SUCCESS)
        self.assertEqual(ing.state, Ingestor.STATES.NEW)

        ing.run()

        self.assertEqual(ing.status, Ingestor.STATUSES.STOPPED)
        self.assertEqual(ing.state, Ingestor.STATES.FINISHED)
        self.assertDictContainsSubset(
            {'before': True, 'after': True}, ing.result
        )

    def test_ingest_failure(self):
        fio = {'fake_file_io': True}
        ing = MyFailedIngestor(fio, file_path='myfile.txt')

        self.assertEqual(ing.status, Ingestor.STATUSES.SUCCESS)
        self.assertEqual(ing.state, Ingestor.STATES.NEW)

        ing.run()

        self.assertEqual(ing.status, Ingestor.STATUSES.FAILURE)
        self.assertEqual(ing.state, Ingestor.STATES.FINISHED)
        self.assertDictContainsSubset(
            {'before': True, 'after': True}, ing.result
        )
