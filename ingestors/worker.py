import logging
from followthemoney import model
from servicelayer.worker import Worker
from servicelayer.logs import apply_task_context

from ingestors import __version__
from ingestors.store import get_dataset
from ingestors.manager import Manager
from ingestors.analysis import Analyzer

log = logging.getLogger(__name__)
OP_INGEST = "ingest"
OP_ANALYZE = "analyze"


class IngestWorker(Worker):
    """A long running task runner that uses Redis as a task queue"""

    def _ingest(self, dataset, task):
        manager = Manager(dataset, task.stage, task.context)
        entity = model.get_proxy(task.payload)
        log.debug("Ingest: %r", entity)
        try:
            manager.ingest_entity(entity)
        finally:
            manager.close()
        return manager.emitted

    def _analyze(self, dataset, task):
        entity_ids = set(task.payload.get("entity_ids"))
        analyzer = None
        for entity in dataset.partials(entity_id=entity_ids):
            if analyzer is None or analyzer.entity.id != entity.id:
                if analyzer is not None:
                    entity_ids.update(analyzer.flush())
                # log.debug("Analyze: %r", entity)
                analyzer = Analyzer(dataset, entity, task.context)
            analyzer.feed(entity)
        if analyzer is not None:
            entity_ids.update(analyzer.flush())
        return list(entity_ids)

    def handle(self, task):
        apply_task_context(task, version=__version__)
        name = task.context.get("ftmstore", task.job.dataset.name)
        dataset = get_dataset(name, task.stage.stage)
        try:
            if task.stage.stage == OP_INGEST:
                entity_ids = self._ingest(dataset, task)
                payload = {"entity_ids": entity_ids}
                self.dispatch_pipeline(task, payload)
            elif task.stage.stage == OP_ANALYZE:
                entity_ids = self._analyze(dataset, task)
                payload = {"entity_ids": entity_ids}
                self.dispatch_pipeline(task, payload)
        finally:
            dataset.close()
