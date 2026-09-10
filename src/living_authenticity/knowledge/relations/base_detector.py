"""Abstract relation detector contract for analytical relation detection.

Relation detection is a read-only analytical stage. It must never decide
actions, authorize changes, mutate units, or perform I/O.
"""

from abc import ABC, abstractmethod
from collections.abc import Sequence

from src.living_authenticity.knowledge.comparison.outcome import ComparisonResult
from src.living_authenticity.knowledge.extraction.knowledge_unit import KnowledgeUnit


class KnowledgeRelationDetector(ABC):
    """Propose analytical relationships from comparison evidence."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Stable strategy name recorded on detection results."""
        raise NotImplementedError

    @abstractmethod
    def detect(
        self, query: KnowledgeUnit, comparisons: Sequence[ComparisonResult]
    ):
        """Return one analytical relation detection result for ``query``."""
        raise NotImplementedError
