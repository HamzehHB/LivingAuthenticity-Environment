from abc import ABC, abstractmethod

from src.living_authenticity.knowledge.ingestion.extraction.knowledge_unit import (
    KnowledgeUnit,
)

from .result import ClassificationResult


class KnowledgeUnitClassifier(ABC):
    """Propose a knowledge-management type for a single knowledge unit.

    Classification is an analytical proposal. It must never:

    * mutate the source :class:`KnowledgeUnit`;
    * write to the filesystem;
    * modify authoritative state;
    * invent evidence;
    * fabricate certainty when the evidence is insufficient.

    A classifier that cannot decide with confidence must say so explicitly
    (an unresolved :class:`ClassificationResult` with ``is_certain=False``).
    """

    @abstractmethod
    def classify(self, unit: KnowledgeUnit) -> ClassificationResult:
        """Return a classification proposal for one knowledge unit."""
        raise NotImplementedError