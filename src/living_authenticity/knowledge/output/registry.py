"""Registry of named Obsidian output generators."""
from .base_generator import ObsidianNoteGenerator
from .evidence_note import DefaultOutputGenerator


class OutputGeneratorRegistry:
    """Hold named output generators."""

    def __init__(self, name: str = "default", generator=None) -> None:
        self._name = name
        default = generator if generator is not None else DefaultOutputGenerator()
        self._items = {name: default}

    def register(self, name: str, generator: ObsidianNoteGenerator) -> None:
        if name in self._items:
            raise ValueError("already registered: " + name)
        self._items[name] = generator

    def get(self, name: str):
        if name not in self._items:
            raise ValueError("unknown generator: " + name)
        item = self._items[name]
        if item is None:
            raise ValueError("generator missing: " + name)
        return item

    def default(self):
        return self.get(self._name)
