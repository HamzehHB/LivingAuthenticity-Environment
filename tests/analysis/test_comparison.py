"""Comparison analysis tests part 1."""

from dataclasses import FrozenInstanceError, asdict

import pytest

from src.living_authenticity.knowledge.analysis.comparison import (
    COMPARISON_CATEGORIES,
    ComparisonResult,
    TokenOverlapComparator,
    comparison_tokens,
    normalize_text,
)
from src.living_authenticity.knowledge.ingestion.extraction.knowledge_unit import KnowledgeUnit
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


def _compare(query_body, cand_body):
    comp = TokenOverlapComparator()
    return comp.compare(_unit(query_body, id="q"), [_cand(cand_body)])[0]


class TestCategories:
    def test_identical_content(self):
        r = _compare("calmness restores the mind", "calmness restores the mind")
        assert r.category == "identical_content"

    def test_possible_duplicate(self):
        r = _compare(
            "calmness restores the mind fully",
            "calmness restores the mind fully today",
        )
        assert r.category == "possible_duplicate"

    def test_related_but_distinct(self):
        r = _compare(
            "calmness restores the mind and body balance",
            "calmness restores the mind during evening practice",
        )
        assert r.category == "related_but_distinct"

    def test_distinct(self):
        r = _compare("calmness restores the mind", "engine repair manual tractor")
        assert r.category == "distinct"

    def test_empty_query(self):
        assert _compare("", "calmness mind").category == "insufficient_evidence"

    def test_empty_candidate(self):
        assert _compare("calmness mind", "").category == "insufficient_evidence"

    def test_closed_set(self):
        assert set(COMPARISON_CATEGORIES) == {
            "identical_content", "possible_duplicate",
            "related_but_distinct", "distinct", "insufficient_evidence",
        }

class TestMultilingual:
    def test_persian_identical(self):
        body = "calmness mind test body"
        r = _compare(body, body)
        assert r.category == "identical_content"

    def test_english_case_insensitive(self):
        r = _compare("Calmness Mind", "calmness mind")
        assert r.category == "identical_content"



class TestEvidence:
    def test_shared_and_residual(self):
        r = _compare("calmness restores mind", "calmness restores body")
        assert "calmness" in r.shared_terms
        assert r.overlap_count == len(r.shared_terms)
        assert r.shared_terms == tuple(sorted(r.shared_terms))
        assert "mind" in r.query_only_terms
        assert "body" in r.candidate_only_terms

    def test_provenance(self):
        q = _unit("calmness mind", id="q1", source="q.md", position=3)
        c = _cand("calmness mind", id="c9", source="kb.md", position=7)
        (r,) = TokenOverlapComparator().compare(q, [c])
        assert (r.query_unit_id, r.query_source, r.query_position) == ("q1", "q.md", 3)
        assert (r.candidate_unit_id, r.candidate_source) == ("c9", "kb.md")
        assert r.candidate_position == 7
        assert r.strategy == "token_overlap_comparison"

    def test_multi_order(self):
        q = _unit("calmness restores mind", id="q")
        cands = [_cand("calmness restores mind", id="c1"), _cand("tractor engine", id="c2")]
        results = TokenOverlapComparator().compare(q, cands)
        assert [r.candidate_unit_id for r in results] == ["c1", "c2"]
        assert results[0].category == "identical_content"
        assert results[1].category == "distinct"

    def test_deterministic(self):
        a = _compare("calmness restores mind body", "calmness restores mind evening")
        b = _compare("calmness restores mind body", "calmness restores mind evening")
        assert asdict(a) == asdict(b)

    def test_empty_list(self):
        assert TokenOverlapComparator().compare(_unit("text"), []) == ()

    def test_lookup_prefers_store(self):
        q = _unit("calmness restores mind", id="q")
        c = _cand("STALE", id="c", source="kb.md", position=1)
        store_unit = _unit("calmness restores mind", id="c", source="kb.md", position=1)
        (r,) = TokenOverlapComparator().compare(q, [c], lookup={"c": store_unit})
        assert r.candidate_text == "calmness restores mind"
        assert r.category == "identical_content"

    def test_frozen(self):
        r = _compare("calmness mind", "calmness mind")
        with pytest.raises(FrozenInstanceError):
            r.category = "x"

    def test_no_action_fields(self):
        payload = asdict(_compare("calmness mind", "calmness mind"))
        for f in ("approved", "authorized", "action", "confidence", "proposal"):
            assert f not in payload


class TestImmutable:
    def test_no_mutation(self):
        q = _unit("calmness mind", id="q")
        c = _cand("calmness mind body", id="c")
        bq, bc = asdict(q), asdict(c)
        TokenOverlapComparator().compare(q, [c])
        assert asdict(q) == bq
        assert asdict(c) == bc


class TestLanguages:
    def test_persian(self):
        body = "Aramesh baraye zohn"
        assert _compare(body, body).category == "identical_content"

    def test_zwnj(self):
        a = "ab" + chr(0x200C) + "cd calmness"
        b = "ab cd calmness"
        assert normalize_text(a) == normalize_text(b)

    def test_mixed(self):
        r = _compare("calmness mind", "calmness mind")
        assert r.category == "identical_content"

    def test_tokens(self):
        assert comparison_tokens("mind mind calmness") == ("calmness", "mind")


class TestInvalid:
    def test_bad_query(self):
        with pytest.raises(TypeError):
            TokenOverlapComparator().compare("nope", [])  # type: ignore[arg-type]

    def test_bad_candidate(self):
        with pytest.raises(TypeError):
            TokenOverlapComparator().compare(_unit("text"), ["nope"])

    def test_none_candidates(self):
        with pytest.raises(TypeError):
            TokenOverlapComparator().compare(_unit("text"), None)  # type: ignore[arg-type]


class TestContract:
    def test_abstract(self):
        from src.living_authenticity.knowledge.analysis.comparison import KnowledgeComparator
        with pytest.raises(TypeError):
            KnowledgeComparator()  # type: ignore[abstract]

    def test_registry(self):
        from src.living_authenticity.knowledge.analysis.comparison import ComparatorRegistry
        reg = ComparatorRegistry()
        assert isinstance(reg.default(), TokenOverlapComparator)
        custom = TokenOverlapComparator()
        reg.register("custom", custom)
        assert reg.get("custom") is custom
        with pytest.raises(ValueError):
            reg.register("default", TokenOverlapComparator())
        with pytest.raises(ValueError):
            reg.get("missing")

    def test_end_to_end(self):
        from src.living_authenticity.knowledge.analysis.retrieval import TokenOverlapRetriever
        corpus = [_unit("calmness restores the mind slowly", id="c1", source="a.md")]
        query = _unit("calmness restores the mind", id="q")
        retrieval = TokenOverlapRetriever().retrieve(query, corpus)
        assert retrieval.has_candidates
        results = TokenOverlapComparator().compare(
            query, retrieval.candidates, lookup={"c1": corpus[0]})
        assert isinstance(results[0], ComparisonResult)
