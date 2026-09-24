"""Registry of named knowledge comparators."""

from .base_comparator import KnowledgeComparator
from .token_overlap import DefaultComparator


class ComparatorRegistry:
    def __init__(self, name: str = "default", comparator=None) -> None:
        self._name = name
        default = comparator if comparator is not None else DefaultComparator()
        self._items = {name: default}

    def register(self, name: str, comparator: KnowledgeComparator) -> None:
        if name in self._items:
            raise ValueError("already registered: " + name)
        self._items[name] = comparator

    def get(self, name: str):
        if name not in self._items:
            raise ValueError("unknown comparator: " + name)
        item = self._items[name]
        if item is None:
            raise ValueError("comparator missing: " + name)
        return item

    def default(self):
        return self.get(self._name)
