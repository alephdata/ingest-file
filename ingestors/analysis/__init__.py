from ingestors.log import get_logger
from itertools import chain
from pprint import pprint  # noqa
from followthemoney import model
from followthemoney.types import registry
from followthemoney.util import make_entity_id
from followthemoney.namespace import Namespace

from ingestors import settings
from ingestors.analysis.aggregate import TagAggregatorFasttext
from ingestors.analysis.aggregate import TagAggregator
from ingestors.analysis.extract import extract_entities
from ingestors.analysis.patterns import extract_patterns
from ingestors.analysis.language import detect_languages
from ingestors.analysis.util import TAG_COMPANY, TAG_PERSON
from ingestors.analysis.util import text_chunks, ANALYZABLE, DOCUMENT

log = get_logger(__name__)


class Analyzer(object):
    MENTIONS = {TAG_COMPANY: "Organization", TAG_PERSON: "Person"}

    def __init__(self, dataset, entity, context):
        self.dataset = dataset
        self.ns = Namespace(context.get("namespace", dataset.name))
        self.entity = model.make_entity(entity.schema)
        self.entity.id = entity.id
        self.aggregator_entities = TagAggregatorFasttext()
        self.aggregator_patterns = TagAggregator()

    def feed(self, entity):
        if not settings.ANALYZE_ENTITIES:
            return
        if not entity.schema.is_a(ANALYZABLE):
            return
        # HACK: Tables should be mapped, don't try to tag them here.
        if entity.schema.is_a("Table"):
            return

        texts = entity.get_type_values(registry.text)
        for text in text_chunks(texts):
            detect_languages(self.entity, text)
            for (prop, tag) in extract_entities(self.entity, text):
                self.aggregator_entities.add(prop, tag)
            for (prop, tag) in extract_patterns(self.entity, text):
                self.aggregator_patterns.add(prop, tag)

    def flush(self):
        writer = self.dataset.bulk()
        countries = set()
        results = list(
            chain(
                self.aggregator_entities.results(), self.aggregator_patterns.results()
            )
        )

        for (key, prop, values) in results:
            if prop.type == registry.country:
                countries.add(key)

        mention_ids = set()
        for (key, prop, values) in results:
            label = values[0]
            if prop.type == registry.name:
                label = registry.name.pick(values)

            schema = self.MENTIONS.get(prop)
            if schema is not None and self.entity.schema.is_a(DOCUMENT):
                mention = model.make_entity("Mention")
                mention.make_id("mention", self.entity.id, prop, key)
                mention_ids.add(mention.id)
                mention.add("resolved", make_entity_id(key))
                mention.add("document", self.entity.id)
                mention.add("name", values)
                mention.add("detectedSchema", schema)
                mention.add("contextCountry", countries)
                mention = self.ns.apply(mention)
                writer.put(mention)
                # pprint(mention.to_dict())

            self.entity.add(prop, label, cleaned=True, quiet=True)

        if len(results):
            log.debug(
                "Extracted %d prop values, %d mentions [%s]: %s",
                len(results),
                len(mention_ids),
                self.entity.schema.name,
                self.entity.id,
            )
            writer.put(self.entity)
            writer.flush()

        return mention_ids
