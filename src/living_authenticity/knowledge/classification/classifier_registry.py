from .base_classifier import KnowledgeUnitClassifier
from .result import ClassificationResult
from .rule_based_classifier import DefaultClassifier


class ClassifierRegistry:
    """Hold named knowledge-unit classifiers.

    The default rule-based classifier is always available. Additional
    classifiers may be registered under distinct names.
    """

    def __init__(self, name: str = "default", classifier: KnowledgeUnitClassifier | None = None) -> None:
        self._name = name
        self._classifiers = {name: classifier if classifier is not None else DefaultClassifier()}

    def register(self, name: str, classifier: KnowledgeUnitClassifier) -> None:
        if name in self._classifiers:
            raise ValueError(f"a classifier named '{name}' is already registered")
        self._classifiers[name] = classifier

    def get(self, name: str):
        if name not in self._classifiers:
            raise ValueError(f"no classifier registered under '{name}'")
        classifier = self._classifiers[name]
        if classifier is None:
            raise ValueError(f"classifier '{name}' has not been provided")
        return classifier

    def default(self):
        return self.get(self._name)