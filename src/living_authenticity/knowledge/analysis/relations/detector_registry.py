"""Registry of named knowledge relation detectors."""

from .base_detector import KnowledgeRelationDetector
from .token_overlap import DefaultDetector


class DetectorRegistry:
    """Hold named knowledge relation detectors."""

    def __init__(self, name: str = "default", detector=None) -> None:
        self._name = name
        default = detector if detector is not None else DefaultDetector()
        self._items = {name: default}

    def register(self, name: str, detector: KnowledgeRelationDetector) -> None:
        if name in self._items:
            raise ValueError("already registered: " + name)
        self._items[name] = detector

    def get(self, name: str):
        if name not in self._items:
            raise ValueError("unknown detector: " + name)
        item = self._items[name]
        if item is None:
            raise ValueError("detector missing: " + name)
        return item

    def default(self):
        return self.get(self._name)
