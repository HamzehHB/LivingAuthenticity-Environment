"""Deterministic token-overlap relation detection logic."""

from collections.abc import Sequence
from typing import Any

from src.living_authenticity.knowledge.comparison.outcome import ComparisonResult
from src.living_authenticity.knowledge.extraction.knowledge_unit import KnowledgeUnit

from .base_detector import KnowledgeRelationDetector
from .outcome import ProposedRelation, RelationDetectionResult


def to_proposal(comparison: ComparisonResult) -> ProposedRelation:
    """Map one comparison outcome to one conservative relation proposal."""
    category = comparison.category
    shared = tuple(comparison.shared_terms) if comparison.shared_terms else ()
    if category == "related_but_distinct":
        return ProposedRelation(
            candidate_unit_id=comparison.candidate_unit_id,
            candidate_source=comparison.candidate_source,
            candidate_position=comparison.candidate_position,
            relation="related",
            basis="Comparison reports related_but_distinct with shared terms.",
            shared_terms=shared,
            comparison_category=category,
        )
    if category in ("identical_content", "possible_duplicate"):
        return ProposedRelation(
            candidate_unit_id=comparison.candidate_unit_id,
            candidate_source=comparison.candidate_source,
            candidate_position=comparison.candidate_position,
            relation="unresolved",
            basis=(
                "Comparison reports " + category + "; identity-like overlap "
                "does not authorize a relation proposal."
            ),
            shared_terms=shared,
            comparison_category=category,
        )
    if category == "insufficient_evidence":
        return ProposedRelation(
            candidate_unit_id=comparison.candidate_unit_id,
            candidate_source=comparison.candidate_source,
            candidate_position=comparison.candidate_position,
            relation="unresolved",
            basis="Insufficient comparison evidence; no relation proposed.",
            shared_terms=shared,
            comparison_category=category,
        )
    return ProposedRelation(
        candidate_unit_id=comparison.candidate_unit_id,
        candidate_source=comparison.candidate_source,
        candidate_position=comparison.candidate_position,
        relation="no_proposed_relation",
        basis="Comparison reports distinct content; no relation proposed.",
        shared_terms=shared,
        comparison_category=category,
    )


class TokenOverlapRelationDetector(KnowledgeRelationDetector):
    """Detect analytically proposed relations from comparison evidence."""

    def __init__(self) -> None:
        self._name = "token_overlap_relation"

    @property
    def name(self) -> str:
        return self._name

    def detect(
        self, query: KnowledgeUnit, comparisons: Sequence[Any]
    ) -> RelationDetectionResult:
        if not isinstance(query, KnowledgeUnit):
            raise TypeError("query must be a KnowledgeUnit")
        if comparisons is None:
            raise TypeError("comparisons must be a sequence")
        items = list(comparisons)
        for item in items:
            if not isinstance(item, ComparisonResult):
                raise TypeError(
                    "comparisons must hold ComparisonResult objects"
                )
            if item.query_unit_id != query.id:
                raise ValueError("comparison query_unit_id does not match query")
        proposals = tuple(to_proposal(item) for item in items)
        if not proposals:
            note = "No comparison evidence; no relation proposed."
        elif any(p.relation == "related" for p in proposals):
            note = (
                "Analytical proposals only; a proposal is not an "
                "authoritative relation."
            )
        else:
            note = "No relation established from available evidence."
        return RelationDetectionResult(
            query_unit_id=query.id,
            query_source=query.source,
            query_position=query.position,
            strategy=self._name,
            proposals=proposals,
            note=note,
        )


class DefaultDetector(TokenOverlapRelationDetector):
    """Default detector alias preserving token-overlap behavior."""
