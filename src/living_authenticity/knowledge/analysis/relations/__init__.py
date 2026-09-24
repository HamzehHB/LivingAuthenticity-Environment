"""Deterministic analytical relation detection over comparison evidence.

Relation detection is a read-only analytical stage. It proposes possible
relationships for later human-governed stages; it creates, modifies, or
authorizes nothing.
"""

from .base_detector import KnowledgeRelationDetector
from .detector_registry import DetectorRegistry
from .outcome import (
    PROPOSED_RELATIONS,
    ProposedRelation,
    RelationDetectionResult,
)
from .token_overlap import DefaultDetector, TokenOverlapRelationDetector

__all__ = (
    "PROPOSED_RELATIONS",
    "ProposedRelation",
    "RelationDetectionResult",
    "KnowledgeRelationDetector",
    "DetectorRegistry",
    "TokenOverlapRelationDetector",
    "DefaultDetector",
)
