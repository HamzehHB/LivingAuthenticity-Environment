"""Registry of named Core relevance analyzers."""

from .base_analyzer import CoreRelevanceAnalyzer
from .token_overlap import DefaultCoreAnalyzer


class AnalyzerRegistry:
    """Hold named Core relevance analyzers."""

    def __init__(self, name: str = "default", analyzer=None) -> None:
        self._name = name
        default = analyzer if analyzer is not None else DefaultCoreAnalyzer()
        self._items = {name: default}

    def register(self, name: str, analyzer: CoreRelevanceAnalyzer) -> None:
        if name in self._items:
            raise ValueError("already registered: " + name)
        self._items[name] = analyzer

    def get(self, name: str):
        if name not in self._items:
            raise ValueError("unknown analyzer: " + name)
        item = self._items[name]
        if item is None:
            raise ValueError("analyzer missing: " + name)
        return item

    def default(self):
        return self.get(self._name)
