"""Minimal provider-independent corpus abstraction for retrieval.

Retrieval needs a source of existing knowledge units without depending on
any particular storage technology. :class:`KnowledgeCorpus` is that narrow
contract: anything able to list units can serve as a corpus. The only
implementation shipped here is an in-memory store for tests, fixtures, and
small deterministic runs. Production vector databases, embedding
infrastructure, vault integrations, and external providers are out of scope
and must not be introduced through this module.
"""

from dataclasses import replace
from typing import Protocol, runtime_checkable

from src.living_authenticity.knowledge.extraction.knowledge_unit import (
    KnowledgeUnit,
)


@runtime_checkable
class KnowledgeCorpus(Protocol):
    """Anything able to list existing knowledge units for retrieval."""

    def list_units(self) -> list[KnowledgeUnit]:
        """Return the existing knowledge units available for searching."""
        ...  # pragma: no cover


class InMemoryKnowledgeStore:
    """In-memory corpus of existing knowledge units.

    Defensive copies are stored and returned, so callers can neither mutate
    the store through a retrieved reference nor observe later store changes
    through an earlier listing. Retrieval treats unit content as inert data.
    """

    def __init__(self, units=()) -> None:
        self._units: list[KnowledgeUnit] = []
        for unit in units:
            self.add(unit)

    def add(self, unit: KnowledgeUnit) -> None:
        """Store a defensive copy of ``unit``."""
        if not isinstance(unit, KnowledgeUnit):
            raise TypeError(
                f"only KnowledgeUnit objects can be stored, got {type(unit).__name__}"
            )
        self._units.append(replace(unit, warnings=list(unit.warnings)))

    def list_units(self) -> list[KnowledgeUnit]:
        """Return defensive copies of the stored units, in stored order."""
        return [replace(unit, warnings=list(unit.warnings)) for unit in self._units]

    def __len__(self) -> int:
        return len(self._units)
