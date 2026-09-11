"""Outcome invariant tests: unsupported values coerce conservatively."""

from src.living_authenticity.knowledge.comparison.outcome import (
    COMPARISON_CATEGORIES,
    ComparisonResult,
)
from src.living_authenticity.knowledge.core_analysis.outcome import (
    CORE_RELEVANCE_VALUES,
    CoreAnalysisResult,
)
from src.living_authenticity.knowledge.relations.outcome import (
    PROPOSED_RELATIONS,
    ProposedRelation,
)


def test_comparison_vocab_coerces_unknown_category():
    assert "distinct" in COMPARISON_CATEGORIES
    result = ComparisonResult(
        query_unit_id="q1", query_source="s", query_position=1,
        candidate_unit_id="c1", candidate_source="v", candidate_position=1,
        category="duplicate",
    )
    assert result.category == "insufficient_evidence"
    assert result.has_overlap is False


def test_relation_vocab_coerces_unknown_relation():
    assert "related" in PROPOSED_RELATIONS
    prop = ProposedRelation(
        candidate_unit_id="c1", candidate_source="v",
        candidate_position=1, relation="supports",
    )
    assert prop.relation == "unresolved"


def test_core_vocab_and_authority_fixed():
    assert "potentially_relevant" in CORE_RELEVANCE_VALUES
    result = CoreAnalysisResult(
        query_unit_id="q1", query_source="s", query_position=1,
        relevance="supports", is_authoritative=True,  # type: ignore
        requires_human_review=False,  # type: ignore
    )
    assert result.relevance == "insufficient_evidence"
    assert result.is_authoritative is False
    assert result.requires_human_review is True
    assert result.is_potentially_relevant is False
