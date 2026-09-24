"""Analytical relation detection tests."""

from dataclasses import FrozenInstanceError, asdict

import pytest

from src.living_authenticity.knowledge.analysis.comparison import (
    ComparisonResult,
    TokenOverlapComparator,
)
from src.living_authenticity.knowledge.ingestion.extraction.knowledge_unit import KnowledgeUnit
from src.living_authenticity.knowledge.analysis.relations import (
    PROPOSED_RELATIONS,
    DetectorRegistry,
    KnowledgeRelationDetector,
    RelationDetectionResult,
    TokenOverlapRelationDetector,
)
from src.living_authenticity.knowledge.analysis.retrieval import RetrievedCandidate


def _unit(body="", *, id="q", source="s.md", position=0):
    return KnowledgeUnit(
        id=id, source=source, original_text=body, cleaned_text=body,
        normalized_text=body, meaning=body, context="", position=position,
    )


def _cand(body, *, id="c", source="kb.md", position=1):
    return RetrievedCandidate(
        unit_id=id, source=source, position=position, text=body,
        matched_terms=(), overlap_score=0, retriever="token_overlap",
    )


def _detect(query_body, cand_body, *, qid="q", cid="c"):
    query = _unit(query_body, id=qid)
    (comparison,) = TokenOverlapComparator().compare(
        query, [_cand(cand_body, id=cid)])
    return TokenOverlapRelationDetector().detect(query, [comparison])


class TestMapping:
    def test_related_but_distinct_proposes_related(self):
        result = _detect(
            "calmness restores the mind and body balance",
            "calmness restores the mind during evening practice",
        )
        proposal = result.proposals[0]
        assert proposal.relation == "related"
        assert proposal.comparison_category == "related_but_distinct"
        assert proposal.candidate_unit_id == "c"
        assert result.has_proposals is True

    def test_identical_content_stays_unresolved(self):
        result = _detect("calmness restores the mind", "calmness restores the mind")
        assert result.proposals[0].relation == "unresolved"
        assert result.has_proposals is False

    def test_possible_duplicate_stays_unresolved(self):
        result = _detect(
            "calmness restores the mind fully",
            "calmness restores the mind fully today",
        )
        assert result.proposals[0].comparison_category == "possible_duplicate"
        assert result.proposals[0].relation == "unresolved"

    def test_distinct_proposes_nothing(self):
        result = _detect("calmness restores the mind", "engine repair manual tractor")
        assert result.proposals[0].relation == "no_proposed_relation"
        assert result.has_proposals is False

    def test_insufficient_evidence_stays_unresolved(self):
        result = _detect("", "calmness mind")
        assert result.proposals[0].relation == "unresolved"

    def test_empty_comparisons(self):
        result = TokenOverlapRelationDetector().detect(_unit("calmness mind"), [])
        assert result.proposals == ()
        assert result.has_proposals is False

    def test_closed_vocabulary(self):
        assert set(PROPOSED_RELATIONS) == {
            "related", "no_proposed_relation", "unresolved",
        }



class TestContract:
    def test_provenance(self):
        query = _unit("calmness mind", id="q1", source="q.md", position=3)
        comparison = ComparisonResult(
            query_unit_id="q1", query_source="q.md", query_position=3,
            candidate_unit_id="c9", candidate_source="kb.md",
            candidate_position=7, category="distinct",
        )
        result = TokenOverlapRelationDetector().detect(query, [comparison])
        assert (result.query_unit_id, result.query_source) == ("q1", "q.md")
        assert result.query_position == 3
        assert result.strategy == "token_overlap_relation"

    def test_frozen(self):
        result = _detect("calmness mind", "calmness mind")
        with pytest.raises(FrozenInstanceError):
            result.note = "x"  # type: ignore[misc]
        with pytest.raises(FrozenInstanceError):
            result.proposals[0].relation = "x"  # type: ignore[misc]

    def test_no_authorization_fields(self):
        payload = asdict(_detect("calmness mind", "calmness mind"))
        for field in ("approved", "execute", "action", "confidence",
                      "target_path", "delete", "update", "merge", "archive"):
            assert field not in payload

    def test_no_mutation(self):
        query = _unit("calmness mind", id="q")
        comparison = ComparisonResult(
            query_unit_id="q", query_source="s.md", query_position=0,
            candidate_unit_id="c", candidate_source="kb.md",
            candidate_position=1, category="distinct",
        )
        before_q, before_c = asdict(query), asdict(comparison)
        TokenOverlapRelationDetector().detect(query, [comparison])
        assert asdict(query) == before_q
        assert asdict(comparison) == before_c

    def test_multilingual(self):
        body = "Aramesh baraye zohn"
        assert _detect(body, body).proposals[0].relation == "unresolved"

    def test_query_mismatch_rejected(self):
        query = _unit("calmness mind", id="q")
        comparison = ComparisonResult(
            query_unit_id="other", query_source="s.md", query_position=0,
            candidate_unit_id="c", candidate_source="kb.md",
            candidate_position=1, category="distinct",
        )
        with pytest.raises(ValueError):
            TokenOverlapRelationDetector().detect(query, [comparison])


class TestInvalid:
    def test_bad_query(self):
        with pytest.raises(TypeError):
            TokenOverlapRelationDetector().detect("nope", [])  # type: ignore[arg-type]

    def test_bad_comparison(self):
        with pytest.raises(TypeError):
            TokenOverlapRelationDetector().detect(_unit("t"), ["no"])  # type: ignore[list-item]

    def test_none_comparisons(self):
        with pytest.raises(TypeError):
            TokenOverlapRelationDetector().detect(_unit("t"), None)  # type: ignore[arg-type]


class TestRegistryAndPipeline:
    def test_abstract(self):
        with pytest.raises(TypeError):
            KnowledgeRelationDetector()  # type: ignore[abstract]

    def test_registry(self):
        reg = DetectorRegistry()
        assert isinstance(reg.default(), TokenOverlapRelationDetector)
        custom = TokenOverlapRelationDetector()
        reg.register("custom", custom)
        assert reg.get("custom") is custom
        with pytest.raises(ValueError):
            reg.register("default", TokenOverlapRelationDetector())
        with pytest.raises(ValueError):
            reg.get("missing")

    def test_end_to_end(self):
        from src.living_authenticity.knowledge.analysis.retrieval import TokenOverlapRetriever
        corpus = [_unit("calmness restores the mind slowly", id="c1", source="a.md")]
        query = _unit("calmness restores the mind", id="q")
        retrieval = TokenOverlapRetriever().retrieve(query, corpus)
        comparisons = TokenOverlapComparator().compare(
            query, retrieval.candidates, lookup={"c1": corpus[0]})
        result = TokenOverlapRelationDetector().detect(query, comparisons)
        assert isinstance(result, RelationDetectionResult)
        assert len(result.proposals) == len(comparisons)
