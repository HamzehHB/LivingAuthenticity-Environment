"""Deterministic analytical knowledge filter."""
from src.living_authenticity.knowledge.classification.result import ClassificationResult
from src.living_authenticity.knowledge.comparison.outcome import ComparisonResult
from src.living_authenticity.knowledge.confidence.outcome import ConfidenceAssessment
from src.living_authenticity.knowledge.core_analysis.outcome import CoreAnalysisResult
from src.living_authenticity.knowledge.extraction.knowledge_unit import KnowledgeUnit
from src.living_authenticity.knowledge.proposal.outcome import Proposal
from src.living_authenticity.knowledge.relations.outcome import RelationDetectionResult
from src.living_authenticity.knowledge.retrieval.result import RetrievalResult
from .filter_outcome import FilterOutcome


class KnowledgeFilter:
    """Analytical filtering/boundary signal over proposal evidence."""

    def __init__(self, strategy: str = "analytical_boundary") -> None:
        self._strategy = strategy

    @property
    def name(self) -> str:
        return self._strategy

    def filter(self, query, proposal=None, classification=None, retrieval=None,
               comparisons=(), relation=None, core=None, confidence=None) -> FilterOutcome:
        if not isinstance(query, KnowledgeUnit):
            raise TypeError("query must be a KnowledgeUnit")
        if not isinstance(proposal, Proposal):
            raise TypeError("proposal must be a Proposal")
        if proposal.query_unit_id != query.id:
            raise ValueError("proposal query_unit_id mismatch")
        if classification is not None and not isinstance(classification, ClassificationResult):
            raise TypeError("classification must be ClassificationResult")
        if retrieval is not None and not isinstance(retrieval, RetrievalResult):
            raise TypeError("retrieval must be RetrievalResult")
        items = tuple(comparisons) if comparisons is not None else ()
        for item in items:
            if not isinstance(item, ComparisonResult):
                raise TypeError("comparisons must hold ComparisonResult")
            if item.query_unit_id != query.id:
                raise ValueError("comparison query_unit_id mismatch")
        if relation is not None and not isinstance(relation, RelationDetectionResult):
            raise TypeError("relation must be RelationDetectionResult")
        if core is not None and not isinstance(core, CoreAnalysisResult):
            raise TypeError("core must be CoreAnalysisResult")
        if confidence is not None and not isinstance(confidence, ConfidenceAssessment):
            raise TypeError("confidence must be ConfidenceAssessment")
        verdict, basis, uncertainties, evidence = self._decide(
            proposal, classification, retrieval, items, relation, core, confidence)
        return FilterOutcome(
            query_unit_id=query.id, query_source=query.source,
            query_position=query.position, verdict=verdict,
            recommended_action=proposal.action, basis=basis,
            uncertainties=tuple(uncertainties), evidence=tuple(evidence),
            strategy=self._strategy,
            note=("Analytical boundary signal for human review only; "
                  "not approval, authorization, or execution."),
            is_authoritative=False, requires_human_review=True)

    def _decide(self, proposal, classification, retrieval, items, relation, core, confidence):
        uncertainties = list(proposal.uncertainties)
        evidence = list(proposal.evidence)
        if confidence is not None:
            evidence.append("confidence:" + confidence.level)
            uncertainties.extend(confidence.uncertainties)
        identity_like = any(c.category in ("identical_content", "possible_duplicate") for c in items)
        contradictory = (
            any(c.category in ("identical_content", "possible_duplicate") for c in items)
            and any(c.category in ("distinct", "related_but_distinct") for c in items))
        if contradictory or any(c.category == "insufficient_evidence" for c in items):
            uncertainties.append("filter: comparison evidence unresolved")
        if core is not None and core.relevance == "potentially_relevant":
            uncertainties.append("filter: core relevance potentially relevant")
        if core is not None and core.relevance == "insufficient_evidence":
            uncertainties.append("filter: core relevance unresolved")
        if identity_like:
            return ("do_not_import",
                    "Comparison reports identity-like overlap; the analytical signal is to not import.",
                    tuple(uncertainties), tuple(evidence))
        if proposal.action == "CREATE":
            if confidence is not None and confidence.level == "sufficiently_supported":
                return ("pass_to_review",
                        "Evidence is consistent and records no gaps; passed forward for mandatory human review.",
                        tuple(uncertainties), tuple(evidence))
            return ("hold_for_review",
                    "CREATE is a non-executing proposal held for mandatory human review.",
                    tuple(uncertainties), tuple(evidence))
        if proposal.action == "DO_NOT_IMPORT":
            return ("do_not_import",
                    "Proposal recommends not importing; the signal stays non-executing and reviewable.",
                    tuple(uncertainties), tuple(evidence))
        return ("hold_for_review",
                "Proposal is unresolved; held for mandatory human review.",
                tuple(uncertainties), tuple(evidence))
