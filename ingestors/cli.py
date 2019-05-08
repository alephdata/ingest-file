import os
import click
import logging
from servicelayer.cache import get_redis
from servicelayer.queue import ServiceQueue

from ingestors.manager import Manager
from ingestors.directory import DirectoryIngestor
from ingestors.task_runner import TaskRunner
from ingestors.util import is_file, is_directory

log = logging.getLogger(__name__)


@click.group()
def cli():
    logging.basicConfig(level=logging.DEBUG)


@cli.command()
def process():
    """Start the queue and process tasks as they come. Blocks while waiting"""
    TaskRunner.run()


@cli.command()
def killthekitten():
    """Completely kill redis contents."""
    conn = get_redis()
    conn.flushall()


@cli.command()
@click.option('--languages',
              multiple=True,
              help="language hint: 2-letter language code (ISO 639)")
@click.option('--dataset',
              required=True,
              help="foreign_id of the collection")
@click.argument('path', type=click.Path(exists=True))
def ingest(path, dataset, languages=None):
    context = {'languages': languages}
    conn = get_redis()
    queue = ServiceQueue(conn, ServiceQueue.OP_INGEST, dataset)
    manager = Manager(queue, context)
    if is_file(path):
        entity = manager.make_entity('Document')
        checksum = manager.archive_entity(entity, path)
        entity.make_id(checksum)
        entity.set('fileName', os.path.basename(path))
        manager.queue_entity(entity)
    if is_directory(path):
        DirectoryIngestor.crawl(manager, path)


if __name__ == "__main__":
    cli()
