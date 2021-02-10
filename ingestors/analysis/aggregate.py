import logging
from collections import defaultdict

from ingestors.analysis.ft_type_model import FTTypeModel
from ingestors.settings import NER_TYPE_MODEL_PATH

log = logging.getLogger(__name__)


class TagAggregatorFasttext(object):
    def __init__(self, model_path=NER_TYPE_MODEL_PATH):
        self.values = defaultdict(set)
        self.model = FTTypeModel(model_path)

    def add(self, prop, value):
        if value is None:
            return
        key = prop.type.node_id_safe(value)
        self.values[(key, prop)].add(value)

    def results(self):
        for (key, prop), values in self.values.items():
            values.discard(None)
            if not values:
                continue
            values = list(values)
            labels, confidences = self.model.confidence(values)
            for label, confidence in zip(labels, confidences):
                if label == "trash" or confidence < 0.85:
                    break
            else:
                yield (key, prop, values)

    def __len__(self):
        return len(self.values)


class TagAggregator(object):
    MAX_TAGS = 10000

    def __init__(self):
        self.values = defaultdict(list)

    def add(self, prop, value):
        key = prop.type.node_id_safe(value)
        if key is None:
            return

        if (key, prop) not in self.values:
            if len(self.values) > self.MAX_TAGS:
                return

        self.values[(key, prop)].append(value)

    def results(self):
        for (key, prop), values in self.values.items():
            yield (key, prop, values)

    def __len__(self):
        return len(self.values)
