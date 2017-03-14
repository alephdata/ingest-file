from ingestors.ingestor import Ingestor

from ..support import TestCase


class MyIngestor(Ingestor):

    def configure(self):
        self.test = dict()
        return {'configured': True}

    def convert_file(self, config):
        self.test['convertion_conf'] = config
        return self.fio

    def before(self):
        self.test['before'] = True

    def after(self):
        self.test['after'] = True

    def ingest(self, config):
        return str(self.fio)


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
        ing = MyIngestor(fio, file_name='myfile.txt')

        self.assertEqual(ing.status, Ingestor.STATUSES.SUCCESS)
        self.assertEqual(ing.state, Ingestor.STATES.NEW)

        ing.run()

        self.assertEqual(ing.status, Ingestor.STATUSES.SUCCESS)
        self.assertEqual(ing.state, Ingestor.STATES.FINISHED)
        self.assertEqual(ing.body.strip(), str(fio))
        self.assertEqual(
            ing.test, {
                'before': True,
                'after': True,
                'convertion_conf': {'configured': True}
            })

    def test_ingest_stopped(self):
        fio = {'fake_file_io': True}
        ing = MyStoppedIngestor(fio, file_name='myfile.txt')

        self.assertEqual(ing.status, Ingestor.STATUSES.SUCCESS)
        self.assertEqual(ing.state, Ingestor.STATES.NEW)

        ing.run()

        self.assertEqual(ing.status, Ingestor.STATUSES.STOPPED)
        self.assertEqual(ing.state, Ingestor.STATES.FINISHED)
        self.assertIsNone(ing.body)
        self.assertEqual(
            ing.test, {
                'before': True,
                'after': True,
                'convertion_conf': {'configured': True}
            })

    def test_ingest_failure(self):
        fio = {'fake_file_io': True}
        ing = MyFailedIngestor(fio, file_name='myfile.txt')

        self.assertEqual(ing.status, Ingestor.STATUSES.SUCCESS)
        self.assertEqual(ing.state, Ingestor.STATES.NEW)

        ing.run()

        self.assertEqual(ing.status, Ingestor.STATUSES.FAILURE)
        self.assertEqual(ing.state, Ingestor.STATES.FINISHED)
        self.assertIsNone(ing.body)
        self.assertEqual(
            ing.test, {
                'before': True,
                'after': True,
                'convertion_conf': {'configured': True}
            })
