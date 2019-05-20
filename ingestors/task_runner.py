import logging
import threading
from followthemoney import model
from servicelayer.cache import get_redis
from servicelayer.queue import ServiceQueue as Queue

from ingestors.manager import Manager
from ingestors import settings

log = logging.getLogger(__name__)


class TaskRunner(object):
    """A long running task runner that uses Redis as a task queue"""

    @classmethod
    def handle_task(cls, queue, payload, context):
        try:
            manager = Manager(queue, context)
            entity = model.get_proxy(payload)
            log.debug("Received: %r", entity)
            file_path = manager.get_filepath(entity)
            manager.ingest(file_path, entity)
            manager.close()
        finally:
            queue.task_done()
            status = queue.progress.get()
            if status.get('pending') < 1:
                index_queue = Queue(queue.conn,
                                    Queue.OP_INDEX,
                                    queue.dataset,
                                    priority=queue.priority)
                index_queue.queue_task({}, {})

    @classmethod
    def process(cls):
        conn = get_redis()
        while True:
            task = Queue.get_operation_task(conn, Queue.OP_INGEST)
            queue, payload, context = task
            if queue is None:
                continue
            cls.handle_task(queue, payload, context)

    @classmethod
    def run(cls):
        log.info("Processing queue (%s threads)", settings.INGESTOR_THREADS)
        threads = []
        for i in range(settings.INGESTOR_THREADS):
            t = threading.Thread(target=cls.process)
            t.daemon = True
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
