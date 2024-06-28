import magic
import logging
from timeit import default_timer
from tempfile import mkdtemp
from datetime import datetime
from pkg_resources import get_distribution

from followthemoney import model
from banal import ensure_list
from normality import stringify
from pantomime import normalize_mimetype
from ftmstore.utils import safe_fragment
from servicelayer.archive import init_archive
from servicelayer.archive.util import ensure_path
from servicelayer.extensions import get_extensions
from sentry_sdk import capture_exception
from servicelayer.cache import get_redis
from servicelayer.taskqueue import queue_task, get_rabbitmq_channel
from followthemoney.helpers import entity_filename
from followthemoney.namespace import Namespace
from prometheus_client import Counter, Histogram

from ingestors.directory import DirectoryIngestor
from ingestors.exc import ProcessingException, ENCRYPTED_MSG
from ingestors.util import filter_text, remove_directory
from ingestors import settings

log = logging.getLogger(__name__)

INGESTIONS_SUCCEEDED = Counter(
    "ingestfile_ingestions_succeeded_total",
    "Successful ingestions",
    ["ingestor"],
)
INGESTIONS_FAILED = Counter(
    "ingestfile_ingestions_failed_total",
    "Failed ingestions",
    ["ingestor"],
)
INGESTION_DURATION = Histogram(
    "ingestfile_ingestion_duration_seconds",
    "Ingest duration by ingestor",
    ["ingestor"],
    # The bucket sizes are a rough guess right now, we might want to adjust
    # them later based on observed durations
    buckets=[
        0.005,
        0.01,
        0.025,
        0.05,
        0.1,
        0.25,
        0.5,
        1,
        5,
        15,
        60,
        5 * 60,
        15 * 60,
    ],
)
INGESTED_BYTES = Counter(
    "ingestfile_ingested_bytes_total",
    "Total number of bytes ingested",
    ["ingestor"],
)


class Manager(object):
    """Handles the lifecycle of an ingestor. This can be subclassed to embed it
    into a larger processing framework."""

    #: Indicates that during the processing no errors or failures occured.
    STATUS_SUCCESS = "success"
    #: Indicates occurance of errors during the processing.
    STATUS_FAILURE = "failure"

    MAGIC = magic.Magic(mime=True)

    def __init__(self, dataset, root_task):
        self.conn = get_redis()
        self.dataset = dataset
        self.writer = dataset.bulk()
        self.root_task = root_task
        self.collection_id = root_task.collection_id
        self.context = root_task.context
        self.ns = Namespace(self.context.get("namespace"))
        self.work_path = ensure_path(mkdtemp(prefix="ingestor-"))
        self.emitted = set()

    @property
    def archive(self):
        if not hasattr(settings, "_archive"):
            settings._archive = init_archive()
        return settings._archive

    def make_entity(self, schema, parent=None):
        schema = model.get(schema)
        entity = model.make_entity(schema, key_prefix=self.collection_id)
        self.make_child(parent, entity)
        return entity

    def make_child(self, parent, child):
        """Derive entity properties by knowing it's parent folder."""
        if parent is not None and child is not None:
            # Folder hierarchy:
            child.add("parent", parent.id)
            child.add("ancestors", parent.get("ancestors"))
            child.add("ancestors", parent.id)
            self.apply_context(child, parent)

    def apply_context(self, entity, source):
        # Aleph-specific context data:
        entity.context = {
            "created_at": source.context.get("created_at"),
            "updated_at": source.context.get("updated_at"),
            "role_id": source.context.get("role_id"),
            "mutable": False,
        }

    def emit_entity(self, entity, fragment=None):
        entity = self.ns.apply(entity)
        self.writer.put(entity.to_dict(), fragment)
        self.emitted.add(entity.id)

    def emit_text_fragment(self, entity, texts, fragment):
        texts = [t for t in ensure_list(texts) if filter_text(t)]
        if len(texts):
            doc = self.make_entity(entity.schema)
            doc.id = entity.id
            doc.add("indexText", texts)
            self.emit_entity(doc, fragment=safe_fragment(fragment))

    def auction(self, file_path, entity):
        if not entity.has("mimeType"):
            if file_path.is_dir():
                entity.add("mimeType", DirectoryIngestor.MIME_TYPE)
                return DirectoryIngestor
            entity.add("mimeType", self.MAGIC.from_file(file_path.as_posix()))

        if "application/encrypted" in entity.get("mimeType"):
            raise ProcessingException(ENCRYPTED_MSG)

        best_score, best_cls = 0, None
        for cls in get_extensions("ingestors"):
            score = cls.match(file_path, entity)
            if score > best_score:
                best_score = score
                best_cls = cls

        if best_cls is None:
            raise ProcessingException("Format not supported")
        return best_cls

    def queue_entity(self, entity):
        log.debug("Queue: %r", entity)
        queue_task(
            get_rabbitmq_channel(),
            get_redis(),
            self.collection_id,
            settings.STAGE_INGEST,
            self.root_task.job_id,
            self.context,
            **entity.to_dict(),
        )

    def store(self, file_path, mime_type=None):
        file_path = ensure_path(file_path)
        mime_type = normalize_mimetype(mime_type)
        if file_path is not None and file_path.is_file():
            return self.archive.archive_file(file_path, mime_type=mime_type)

    def load(self, content_hash, file_name=None):
        # log.info("Local archive name: %s", file_name)
        return self.archive.load_file(
            content_hash, file_name=file_name, temp_path=self.work_path
        )

    def ingest_entity(self, entity):
        for content_hash in entity.get("contentHash", quiet=True):
            file_name = entity_filename(entity)
            file_path = self.load(content_hash, file_name=file_name)
            if file_path is None or not file_path.exists():
                log.warning(
                    f"Couldn't find file named {file_name} at path {file_path}."
                    "Skipping ingestion."
                )
                continue
            self.ingest(file_path, entity)
            return
        self.finalize(entity)

    def ingest(self, file_path, entity, **kwargs):
        """Main execution step of an ingestor."""
        file_path = ensure_path(file_path)
        file_size = None

        if file_path.is_file():
            file_size = file_path.stat().st_size  # size in bytes

        if file_size is not None and not entity.has("fileSize"):
            entity.add("fileSize", file_size)

        now = datetime.now()
        now_string = now.strftime("%Y-%m-%dT%H:%M:%S.%f")

        entity.set("processingStatus", self.STATUS_FAILURE)
        entity.set("processingAgent", get_distribution("ingest").version)
        entity.set("processedAt", now_string)

        ingestor_class = None
        ingestor_name = None

        try:
            ingestor_class = self.auction(file_path, entity)
            ingestor_name = ingestor_class.__name__
            log.info(f"Ingestor [{repr(entity)}]: {ingestor_name}")

            start_time = default_timer()
            self.delegate(ingestor_class, file_path, entity)
            duration = max(0, default_timer() - start_time)

            INGESTIONS_SUCCEEDED.labels(ingestor=ingestor_name).inc()
            INGESTION_DURATION.labels(ingestor=ingestor_name).observe(duration)

            if file_size is not None:
                INGESTED_BYTES.labels(ingestor=ingestor_name).inc(file_size)

            entity.set("processingStatus", self.STATUS_SUCCESS)
        except ProcessingException as pexc:
            log.exception(f"[{repr(entity)}] Failed to process: {pexc}")
            INGESTIONS_FAILED.labels(ingestor=ingestor_name).inc()
            entity.set("processingError", stringify(pexc))
            if settings.SENTRY_CAPTURE_PROCESSING_EXCEPTIONS:
                capture_exception(pexc)
        finally:
            self.finalize(entity)

    def finalize(self, entity):
        self.emit_entity(entity)
        self.writer.flush()
        remove_directory(self.work_path)

    def delegate(self, ingestor_class, file_path, entity):
        ingestor_class(self).ingest(file_path, entity)

    def close(self):
        self.writer.flush()
        remove_directory(self.work_path)
