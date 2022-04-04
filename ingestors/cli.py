import sys
import click
import logging
import uuid
from pprint import pprint
from ftmstore import get_dataset
from servicelayer.cache import get_redis, get_fakeredis
from servicelayer.logs import configure_logging
from servicelayer.taskqueue import Dataset, Task
from servicelayer import settings as sl_settings
from servicelayer.archive.util import ensure_path

from ingestors import settings
from ingestors.manager import Manager
from ingestors.directory import DirectoryIngestor
from ingestors.analysis import Analyzer
from ingestors.worker import get_worker, OP_INGEST, OP_ANALYZE

log = logging.getLogger(__name__)


@click.group()
def cli():
    configure_logging(level=logging.DEBUG)


@cli.command()
@click.option("-s", "--sync", is_flag=True, default=False, help="Run without threads")
def process(sync):
    """Start the queue and process tasks as they come. Blocks while waiting"""
    num_threads = None if sync else sl_settings.WORKER_THREADS
    worker = get_worker(num_threads=num_threads)
    code = worker.run()
    sys.exit(code)


@cli.command()
@click.argument("dataset")
def cancel(dataset):
    """Delete scheduled tasks for given dataset"""
    conn = get_redis()
    Dataset(conn, dataset).cancel()


@cli.command()
def killthekitten():
    """Completely kill redis contents."""
    conn = get_redis()
    conn.flushall()


def _ingest_path(db, dataset, path, languages=[]):
    context = {"languages": languages}
    task = Task(
        task_id=uuid.uuid4().hex,
        job_id=uuid.uuid4().hex,
        collection_id=dataset,
        delivery_tag="",
        context=context,
        payload={},
    )
    manager = Manager(db, task)
    path = ensure_path(path)
    if path is not None:
        if path.is_file():
            entity = manager.make_entity("Document")
            checksum = manager.store(path)
            entity.set("contentHash", checksum)
            entity.make_id(checksum)
            entity.set("fileName", path.name)
            log.info("Queue: %r", entity.to_dict())
            manager.queue_entity(entity)
        if path.is_dir():
            DirectoryIngestor.crawl(manager, path)
    manager.close()


@cli.command()
@click.option("--languages", multiple=True, help="3-letter language code (ISO 639)")
@click.option("--dataset", required=True, help="Name of the dataset")
@click.argument("path", type=click.Path(exists=True))
def ingest(path, dataset, languages=None):
    """Queue a set of files for ingest."""
    db = get_dataset(dataset, OP_INGEST)
    _ingest_path(db, dataset, path, languages=languages)


@cli.command()
@click.option("--dataset", required=True, help="Name of the dataset")
def analyze(dataset):
    db = get_dataset(dataset, OP_ANALYZE)
    analyzer = None
    for entity in db.partials():
        if analyzer is None or analyzer.entity.id != entity.id:
            if analyzer is not None:
                analyzer.flush()
            # log.debug("Analyze: %r", entity)
            analyzer = Analyzer(db, entity, {})
        analyzer.feed(entity)
    if analyzer is not None:
        analyzer.flush()


@cli.command()
@click.option("--languages", multiple=True, help="3-letter language code (ISO 639)")
@click.argument("path", type=click.Path(exists=True))
def debug(path, languages=None):
    """Debug the ingest for the given path."""
    conn = get_fakeredis()
    settings.fts.DATABASE_URI = "sqlite:////tmp/debug.sqlite3"
    db = get_dataset("debug", origin=OP_INGEST, database_uri=settings.fts.DATABASE_URI)
    db.delete()
    _ingest_path(db, "debug", path, languages=languages)
    worker = get_worker()
    worker.sync()
    for entity in db.iterate():
        pprint(entity.to_dict())


if __name__ == "__main__":
    cli()
