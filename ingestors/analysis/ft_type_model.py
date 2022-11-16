from ingestors.log import get_logger

import fasttext
import numpy as np
from normality import normalize

from ingestors.util import SingletonDecorator

log = get_logger(__name__)

@SingletonDecorator
class FTTypeModel(object):
    def __init__(self, model_path):
        self.model_path = model_path
        self.model = fasttext.load_model(model_path)
        self.n_labels = len(self.model.get_labels())
        self.max_entropy = -1 * np.log(1.0 / self.n_labels)

    def confidence(self, values):
        labels, scores = self.model.predict(self._clean_input(values), k=-1)
        # confidence = 1 - (entropy / max entropy) ∈ [0, 1]
        confidence = 1 + (scores * np.log(scores)).sum(axis=1) / self.max_entropy
        return list(self._clean_labels(labels)), confidence

    def _clean_input(self, values):
        return [normalize(v, lowercase=True, latinize=True) for v in values]

    def _clean_labels(self, labels):
        for label in labels:
            yield label[0].replace("__label__", "")

