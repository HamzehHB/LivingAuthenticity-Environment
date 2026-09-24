"""Registry of named proposal builders."""

from .builder import ProposalBuilder


class ProposalRegistry:
    """Hold named proposal builders."""

    def __init__(self, name: str = "default", builder=None) -> None:
        self._name = name
        default = builder if builder is not None else ProposalBuilder()
        self._items = {name: default}

    def register(self, name: str, builder: ProposalBuilder) -> None:
        if name in self._items:
            raise ValueError("already registered: " + name)
        self._items[name] = builder

    def get(self, name: str):
        if name not in self._items:
            raise ValueError("unknown builder: " + name)
        item = self._items[name]
        if item is None:
            raise ValueError("builder missing: " + name)
        return item

    def default(self):
        return self.get(self._name)
