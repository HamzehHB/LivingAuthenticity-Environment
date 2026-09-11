"""Proposal system tests: actions, evidence, determinism, boundaries."""

import dataclasses

from src.living_authenticity.knowledge.classification.result import (
    ClassificationResult,
)
from src.living_authenticity.knowledge.comparison.outcome import ComparisonResult
from src.living_authenticity.knowledge.core_analysis.outcome import (
    CoreAnalysisResult,
)
from src.living_authenticity.knowledge.extraction.knowledge_unit import (
    KnowledgeUnit,
)
from src.living_authenticity.knowledge.proposal.builder import ProposalBuilder
from src.living_authenticity.knowledge.proposal.outcome import PROPOSAL_ACTIONS
from src.living_authenticity.knowledge.proposal.registry import ProposalRegistry
from src.living_authenticity.knowledge.relations.outcome import (
    ProposedRelation,
    RelationDetectionResult,
)
from src.living_authenticity.knowledge.retrieval.candidate import (
    RetrievedCandidate,
)
from src.living_authenticity.knowledge.retrieval.result import RetrievalResult


def _unit(uid="q1", text="A calm morning observation about attention"):
    return KnowledgeUnit(
        id=uid, source="inbox", original_text=text,
        meaning=text, cleaned_text=text, normalized_text=text,
        context="", proposed_type="", position=1,
    )


def _cls(certain=True, ptype="Observation"):
    return ClassificationResult(
        unit_id="q1", source="inbox", position=1,
        proposed_type=(ptype if certain else ""),
        is_certain=certain, rationale="r",
        evidence=("e",), classifier="rule_based_default",
    )


def _ret_empty():
    return RetrievalResult(
        query_unit_id="q1", query_source="inbox", query_position=1,
        strategy="token_overlap", candidates=(), corpus_size=3,
        query_terms=("morning",), note="none",
    )


def _ret_with(uid="c1"):
    cand = RetrievedCandidate(
        unit_id=uid, source="vault", position=2, text="other text",
        matched_terms=("text",), overlap_score=1, retriever="token_overlap",
    )
    return RetrievalResult(
        query_unit_id="q1", query_source="inbox", query_position=1,
        strategy="token_overlap", candidates=(cand,), corpus_size=3,
        query_terms=("text",), note="one",
    )


def _cmp(uid="c1", cat="distinct"):
    return ComparisonResult(
        query_unit_id="q1", query_source="inbox", query_position=1,
        candidate_unit_id=uid, candidate_source="vault",
        candidate_position=2, strategy="s", category=cat,
        shared_terms=(), query_only_terms=("a",),
        candidate_only_terms=("b",), overlap_count=0, note="n",
        candidate_text="other text",
    )


def _rel(uid="c1", rel="no_proposed_relation"):
    return RelationDetectionResult(
        query_unit_id="q1", query_source="inbox", query_position=1,
        strategy="s",
        proposals=(ProposedRelation(
            candidate_unit_id=uid, candidate_source="vault",
            candidate_position=2, relation=rel, basis="b",
            shared_terms=(), comparison_category="distinct"),),
        note="n",
    )


def _core(rel="no_observed_relevance"):
    return CoreAnalysisResult(
        query_unit_id="q1", query_source="inbox", query_position=1,
        strategy="s", relevance=rel, basis="b", shared_terms=(),
        examined_core_ids=("core1",), note="n",
        is_authoritative=False, requires_human_review=True, evidence=(),
    )


def test_actions_vocab():
    assert tuple(sorted(PROPOSAL_ACTIONS)) == (
        "CREATE", "DO_NOT_IMPORT", "NEEDS_REVIEW",
    )


def test_valid_create_no_candidates():
    builder = ProposalBuilder()
    proposal = builder.build(
        _unit(), classification=_cls(), retrieval=_ret_empty(),
        comparisons=(), relation=None, core=_core(),
    )
    assert proposal.action == "CREATE"
    assert proposal.is_authoritative is False
    assert proposal.requires_human_review is True


def test_valid_create_distinct():
    builder = ProposalBuilder()
    proposal = builder.build(
        _unit(), classification=_cls(), retrieval=_ret_with(),
        comparisons=(_cmp(),), relation=_rel(), core=_core(),
    )
    assert proposal.action == "CREATE"
    assert proposal.relevant_candidates == ("candidate:c1@vault#2",)


def test_valid_do_not_import():
    builder = ProposalBuilder()
    proposal = builder.build(
        _unit(), classification=_cls(), retrieval=_ret_with(),
        comparisons=(_cmp(cat="identical_content"),),
        relation=_rel(uid="c1", rel="unresolved"), core=_core(),
    )
    assert proposal.action == "DO_NOT_IMPORT"


def test_needs_review_unresolved_cls():
    builder = ProposalBuilder()
    proposal = builder.build(
        _unit(), classification=_cls(certain=False),
        retrieval=_ret_empty(), comparisons=(), relation=None,
        core=_core(),
    )
    assert proposal.action == "NEEDS_REVIEW"


def test_needs_review_core_relevant():
    builder = ProposalBuilder()
    proposal = builder.build(
        _unit(), classification=_cls(), retrieval=_ret_empty(),
        comparisons=(), relation=None,
        core=_core(rel="potentially_relevant"),
    )
    assert proposal.action == "NEEDS_REVIEW"
    assert proposal.core_relevance == "potentially_relevant"


def test_needs_review_contradictory():
    builder = ProposalBuilder()
    proposal = builder.build(
        _unit(), classification=_cls(), retrieval=_ret_with("c1"),
        comparisons=(_cmp("c1", "possible_duplicate"),
                     _cmp("c2", "distinct")),
        relation=_rel(), core=_core(),
    )
    assert proposal.action == "NEEDS_REVIEW"


def test_needs_review_insufficient():
    builder = ProposalBuilder()
    proposal = builder.build(
        _unit(), classification=_cls(), retrieval=_ret_with(),
        comparisons=(_cmp(cat="insufficient_evidence"),),
        relation=_rel(), core=_core(),
    )
    assert proposal.action == "NEEDS_REVIEW"


def test_needs_review_related():
    builder = ProposalBuilder()
    proposal = builder.build(
        _unit(), classification=_cls(), retrieval=_ret_with(),
        comparisons=(_cmp(cat="related_but_distinct"),),
        relation=_rel(uid="c1", rel="related"), core=_core(),
    )
    assert proposal.action == "NEEDS_REVIEW"


def test_provenance_and_evidence():
    proposal = ProposalBuilder().build(
        _unit(), classification=_cls(), retrieval=_ret_with(),
        comparisons=(_cmp(),), relation=_rel(), core=_core(),
    )
    assert proposal.query_unit_id == "q1"
    assert any(e.startswith("classification:") for e in proposal.evidence)
    assert any(e.startswith("comparison:") for e in proposal.evidence)
    assert any(e.startswith("core:") for e in proposal.evidence)
    assert proposal.provenance[0].startswith("query:q1@")


def test_inputs_not_mutated():
    query = _unit()
    snap = (query.id, query.source, query.cleaned_text, query.position)
    retr = _ret_with()
    cmps = (_cmp(),)
    ProposalBuilder().build(query, _cls(), retr, cmps, _rel(), _core())
    assert (query.id, query.source, query.cleaned_text, query.position) == snap
    assert len(retr.candidates) == 1 and len(cmps) == 1


def test_immutable_proposal():
    proposal = ProposalBuilder().build(
        _unit(), classification=_cls(), retrieval=_ret_empty(),
        comparisons=(), relation=None, core=_core(),
    )
    try:
        proposal.action = "CREATE"  # type: ignore
        raise AssertionError("proposal must be frozen")
    except dataclasses.FrozenInstanceError:
        pass


def test_deterministic_ordering():
    retr = RetrievalResult(
        query_unit_id="q1", query_source="inbox", query_position=1,
        strategy="s",
        candidates=(
            RetrievedCandidate(unit_id="c2", source="vault", position=3,
                               text="t", matched_terms=("t",),
                               overlap_score=1, retriever="r"),
            RetrievedCandidate(unit_id="c1", source="vault", position=2,
                               text="t", matched_terms=("t",),
                               overlap_score=1, retriever="r"),
        ),
        corpus_size=2, query_terms=("t",), note="n",
    )
    cmps = (_cmp("c2"), _cmp("c1"))
    cls = _cls()
    rel = _rel()
    core = _core()
    first = ProposalBuilder().build(
        _unit(), classification=cls, retrieval=retr,
        comparisons=cmps, relation=rel, core=core,
    )
    second = ProposalBuilder().build(
        _unit(), classification=cls, retrieval=retr,
        comparisons=cmps, relation=rel, core=core,
    )
    assert first == second
    assert first.relevant_candidates == (
        "candidate:c1@vault#2", "candidate:c2@vault#3",
    )


def test_malformed_rejected():
    builder = ProposalBuilder()
    try:
        builder.build("nope")  # type: ignore
        raise AssertionError("expected TypeError")
    except TypeError:
        pass
    try:
        builder.build(_unit(), comparisons=("x",))  # type: ignore
        raise AssertionError("expected TypeError")
    except TypeError:
        pass
    bad = ComparisonResult(
        query_unit_id="other", query_source="inbox", query_position=1,
        candidate_unit_id="c1", candidate_source="v", candidate_position=1,
    )
    try:
        builder.build(_unit(), comparisons=(bad,))
        raise AssertionError("expected ValueError")
    except ValueError:
        pass


def test_registry_behaviour():
    reg = ProposalRegistry()
    assert isinstance(reg.default(), ProposalBuilder)
    reg.register("extra", ProposalBuilder(strategy="extra"))
    assert reg.get("extra").name == "extra"
    try:
        reg.register("extra", ProposalBuilder())
        raise AssertionError("expected duplicate error")
    except ValueError:
        pass
