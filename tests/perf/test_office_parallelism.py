# -*- coding: utf-8 -*-
import io
import multiprocessing
from threading import Thread

from ingestors import DocumentIngestor

from ..support import TestCase


class ThreadedDocumentIngestor(DocumentIngestor, Thread):

    def __init__(self, *args, **kwargs):
        super(ThreadedDocumentIngestor, self).__init__(*args, **kwargs)
        Thread.__init__(self)


class OfficeParallelismTest(TestCase):

    def test_doc_to_pdf(self):
        ingestors = []
        queue_size = multiprocessing.cpu_count() + 1
        fixture_path = self.fixture('documents/hello world word.docx')

        for num in range(queue_size):
            with io.open(fixture_path, mode='rb') as fio:
                ingestor = ThreadedDocumentIngestor(fio, fixture_path)
                ingestors.append(ingestor)
                ingestor.start()

        self.assertTrue(map(lambda i: i.join(), ingestors))
        self.assertEqual(len(ingestors), queue_size)

        for ingestor in ingestors:
            self.assertEqual(
                ingestor.status, DocumentIngestor.STATUSES.SUCCESS)
