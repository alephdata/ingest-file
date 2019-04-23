import logging
import os

import click
from servicelayer.archive import init_archive
from servicelayer.cache import get_redis
from servicelayer.queue import push_task
from servicelayer import settings

from ingestors.task_runner import TaskRunner
from ingestors.util import is_file, make_entity

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
    if not is_file(path):
        raise click.BadParameter('path is not a file')
    archive = init_archive()
    entity = make_entity('Document', dataset)
    checksum = archive.archive_file(path)
    entity.id = checksum
    entity.set('contentHash', checksum)
    entity.set('fileSize', os.path.getsize(path))
    file_name = os.path.basename(path)
    entity.set('fileName', file_name)
    context = {
        'languages': languages
    }
    push_task(settings.QUEUE_HIGH, dataset, entity.to_dict(), context)


if __name__ == "__main__":
    cli()
