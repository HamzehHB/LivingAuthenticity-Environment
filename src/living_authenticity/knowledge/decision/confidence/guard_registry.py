"""Registry of named confidence guards."""

from .base_guard import ConfidenceGuard
from .evidence_strength import DefaultConfidenceGuard


class ConfidenceGuardRegistry:
    """Hold named confidence guards."""

    def __init__(self, name: str = "default", guard=None) -> None:
        self._name = name
        default = guard if guard is not None else DefaultConfidenceGuard()
        self._items = {name: default}

    def register(self, name: str, guard: ConfidenceGuard) -> None:
        if name in self._items:
            raise ValueError("already registered: " + name)
        self._items[name] = guard

    def get(self, name: str):
        if name not in self._items:
            raise ValueError("unknown guard: " + name)
        item = self._items[name]
        if item is None:
            raise ValueError("guard missing: " + name)
        return item

    def default(self):
        return self.get(self._name)
