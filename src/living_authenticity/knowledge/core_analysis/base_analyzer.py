"""Abstract Core relevance analyzer contract.

Core Analysis is a read-only analytical stage. It must never decide
actions, authorize changes, mutate units, modify Core, or perform I/O.
"""

from abc import ABC, abstractmethod
from collections.abc import Sequence

from src.living_authenticity.knowledge.extraction.knowledge_unit import KnowledgeUnit


class CoreRelevanceAnalyzer(ABC):
    """Produce an analytical Core relevance observation for one query unit."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Stable strategy name recorded on analysis results."""
        raise NotImplementedError

    @abstractmethod
    def analyze(self, query: KnowledgeUnit, core_units: Sequence[KnowledgeUnit]):
        """Return one analytical Core relevance result for ``query``."""
        raise NotImplementedError
