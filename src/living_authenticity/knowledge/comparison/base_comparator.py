"""Abstract comparator contract for analytical knowledge comparison.

Comparison is a read-only analytical stage. It must never decide actions,
authorize changes, mutate units, or perform I/O.
"""

from abc import ABC, abstractmethod
from collections.abc import Sequence

from src.living_authenticity.knowledge.extraction.knowledge_unit import KnowledgeUnit
from src.living_authenticity.knowledge.retrieval.candidate import RetrievedCandidate


class KnowledgeComparator(ABC):
    """Compare one query unit against retrieved candidate evidence."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Stable strategy name recorded on comparison results."""
        raise NotImplementedError

    @abstractmethod
    def compare(
        self, query: KnowledgeUnit, candidates: Sequence[RetrievedCandidate]
    ):
        """Return one analytical comparison result per candidate, in order."""
        raise NotImplementedError
