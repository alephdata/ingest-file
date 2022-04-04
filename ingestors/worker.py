import logging
import json
from pprint import pformat  # noqa
import uuid
import threading

import pika
from banal import ensure_list
from followthemoney import model
from ftmstore import get_dataset
from servicelayer.cache import get_redis
from servicelayer.taskqueue import (
    Worker,
    Task,
    Dataset,
    dataset_from_collection_id,
    QUEUE_INGEST,
    get_routing_key,
    OP_ANALYZE,
    OP_INGEST,
    get_rabbitmq_channel,
)

from ingestors import __version__
from ingestors.manager import Manager
from ingestors.analysis import Analyzer

log = logging.getLogger(__name__)


threadlocal = threading.local()
threadlocal.channel = get_rabbitmq_channel()


# ToDo: Move to servicelayer??
def queue_task(collection_id, stage, job_id=None, context=None, **payload):
    task_id = uuid.uuid4().hex
    body = {
        "collection_id": dataset_from_collection_id(collection_id),
        "job_id": job_id,
        "task_id": task_id,
        "operation": stage,
        "context": context,
        "payload": payload,
    }

    try:
        threadlocal.channel.basic_publish(
            exchange="",
            routing_key=get_routing_key(body["operation"]),
            body=json.dumps(body),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
        dataset = Dataset(
            conn=get_redis(), name=dataset_from_collection_id(collection_id)
        )
        dataset.add_task(task_id)
    except pika.exceptions.UnroutableError:
        log.exception("Error while queuing task")


class IngestWorker(Worker):
    """A long running task runner that uses Redis as a task queue"""

    def _ingest(self, ftmstore_dataset, task: Task):
        manager = Manager(ftmstore_dataset, task)
        entity = model.get_proxy(task.payload)
        log.debug("Ingest: %r", entity)
        try:
            manager.ingest_entity(entity)
        finally:
            manager.close()
        return list(manager.emitted)

    def _analyze(self, ftmstore_dataset, task: Task):
        entity_ids = set(task.payload.get("entity_ids"))
        analyzer = None
        for entity in ftmstore_dataset.partials(entity_id=entity_ids):
            if analyzer is None or analyzer.entity.id != entity.id:
                if analyzer is not None:
                    entity_ids.update(analyzer.flush())
                # log.debug("Analyze: %r", entity)
                analyzer = Analyzer(ftmstore_dataset, entity, task.context)
            analyzer.feed(entity)
        if analyzer is not None:
            entity_ids.update(analyzer.flush())
        return list(entity_ids)

    def dispatch_task(self, task: Task):
        name = task.context.get("ftmstore", task.collection_id)
        ftmstore_dataset = get_dataset(name, task.operation)
        if task.operation == OP_INGEST:
            entity_ids = self._ingest(ftmstore_dataset, task)
            payload = {"entity_ids": entity_ids}
            self.dispatch_pipeline(task, payload)
        elif task.operation == OP_ANALYZE:
            entity_ids = self._analyze(ftmstore_dataset, task)
            payload = {"entity_ids": entity_ids}
            self.dispatch_pipeline(task, payload)

    def dispatch_pipeline(self, task: Task, payload):
        """Some queues use a continuation passing style pipeline argument
        to specify the next steps for a processing chain."""
        pipeline = ensure_list(task.context.get("pipeline"))
        if len(pipeline) == 0:
            return
        next_stage = pipeline.pop(0)
        context = dict(task.context)
        context["pipeline"] = pipeline

        queue_task(
            task.collection_id,
            next_stage,
            task.job_id,
            context,
            **payload,
        )


def get_worker(num_threads=None):
    operations = [OP_ANALYZE, OP_INGEST]
    log.info(f"Worker active, stages: {operations}")
    return IngestWorker(
        queues=[
            QUEUE_INGEST,
        ],
        conn=get_redis(),
        version=__version__,
        num_threads=num_threads,
    )
