"""Confidence tests: levels, determinism, non-mutation, boundaries."""

import copy
import dataclasses

from src.living_authenticity.knowledge.decision.confidence.evidence_strength import (
    DefaultConfidenceGuard,
    EvidenceStrengthGuard,
)
from src.living_authenticity.knowledge.decision.confidence.guard_registry import (
    ConfidenceGuardRegistry,
)
from src.living_authenticity.knowledge.decision.confidence.outcome import (
    CONFIDENCE_LEVELS,
    ConfidenceAssessment,
)
from src.living_authenticity.knowledge.decision.proposal.builder import ProposalBuilder

from tests.decision.test_proposal import (
    _cls,
    _cmp,
    _core,
    _rel,
    _ret_empty,
    _ret_with,
    _unit,
)


_USE_DEFAULT = object()


def _proposal(classification=_USE_DEFAULT, retrieval=_USE_DEFAULT,
              comparisons=_USE_DEFAULT, relation=_USE_DEFAULT,
              core=_USE_DEFAULT, destination=""):
    if classification is _USE_DEFAULT:
        classification = _cls()
    if retrieval is _USE_DEFAULT:
        retrieval = _ret_with()
    if comparisons is _USE_DEFAULT:
        comparisons = (_cmp(),)
    if relation is _USE_DEFAULT:
        relation = _rel()
    if core is _USE_DEFAULT:
        core = _core()
    return ProposalBuilder().build(
        _unit(), classification=classification, retrieval=retrieval,
        comparisons=comparisons, relation=relation, core=core,
        destination=destination,
    )


def test_levels_vocab():
    assert tuple(CONFIDENCE_LEVELS) == (
        "sufficiently_supported", "weak",
        "contradictory_or_unresolved", "insufficient_evidence",
    )


def test_sufficiently_supported_distinct_evidence():
    result = DefaultConfidenceGuard().assess(
        _unit(), _proposal(), classification=_cls(),
        retrieval=_ret_with(), comparisons=(_cmp(),),
        relation=_rel(), core=_core(),
    )
    assert result.level == "sufficiently_supported"
    assert result.is_sufficiently_supported is True
    assert result.proposal_action == "CREATE"
    assert result.is_authoritative is False
    assert result.requires_human_review is True


def test_weak_gap_evidence():
    proposal = _proposal(retrieval=_ret_empty(), comparisons=())
    result = DefaultConfidenceGuard().assess(
        _unit(), proposal, classification=_cls(),
        retrieval=_ret_empty(), comparisons=(), relation=None,
        core=_core(),
    )
    assert result.level == "weak"
    assert result.is_sufficiently_supported is False
    assert result.uncertainties


def test_insufficient_no_evidence():
    proposal = ProposalBuilder().build(_unit())
    result = DefaultConfidenceGuard().assess(_unit(), proposal)
    assert result.level == "insufficient_evidence"


def test_contradictory_evidence():
    proposal = _proposal(
        comparisons=(_cmp("c1", "possible_duplicate"),
                     _cmp("c2", "distinct")),
    )
    result = DefaultConfidenceGuard().assess(
        _unit(), proposal, classification=_cls(),
        retrieval=_ret_with(), comparisons=(
            _cmp("c1", "possible_duplicate"), _cmp("c2", "distinct")),
        relation=_rel(), core=_core(),
    )
    assert result.level == "contradictory_or_unresolved"
    assert result.proposal_action == "NEEDS_REVIEW"


def test_unresolved_comparison_evidence():
    proposal = _proposal(comparisons=(_cmp(cat="insufficient_evidence"),))
    result = DefaultConfidenceGuard().assess(
        _unit(), proposal, classification=_cls(),
        retrieval=_ret_with(),
        comparisons=(_cmp(cat="insufficient_evidence"),),
        relation=_rel(), core=_core(),
    )
    assert result.level == "contradictory_or_unresolved"


def test_unknown_level_coerces():
    result = ConfidenceAssessment(
        query_unit_id="q1", query_source="s", query_position=1,
        level="certain", is_authoritative=True,  # type: ignore
        requires_human_review=False,  # type: ignore
    )
    assert result.level == "insufficient_evidence"
    assert result.is_sufficiently_supported is False
    assert result.is_authoritative is False
    assert result.requires_human_review is True


def test_no_authorization_fields():
    result = DefaultConfidenceGuard().assess(
        _unit(), _proposal(), classification=_cls(),
        retrieval=_ret_with(), comparisons=(_cmp(),),
        relation=_rel(), core=_core(),
    )
    payload = dataclasses.asdict(result)
    for field in ("approved", "authorized", "execution_allowed",
                  "safe_to_execute", "human_approved", "action",
                  "confidence", "target_path"):
        assert field not in payload


def test_deterministic_assessment():
    first = DefaultConfidenceGuard().assess(
        _unit(), _proposal(), classification=_cls(),
        retrieval=_ret_with(), comparisons=(_cmp(),),
        relation=_rel(), core=_core(),
    )
    second = DefaultConfidenceGuard().assess(
        _unit(), _proposal(), classification=_cls(),
        retrieval=_ret_with(), comparisons=(_cmp(),),
        relation=_rel(), core=_core(),
    )
    assert first == second


def test_inputs_not_mutated():
    proposal = _proposal()
    snapshot = copy.deepcopy(proposal)
    retr = _ret_with()
    cmps = (_cmp(),)
    DefaultConfidenceGuard().assess(
        _unit(), proposal, classification=_cls(),
        retrieval=retr, comparisons=cmps, relation=_rel(), core=_core(),
    )
    assert proposal == snapshot
    assert len(retr.candidates) == 1 and len(cmps) == 1


def test_immutable_outcome():
    result = DefaultConfidenceGuard().assess(_unit(), _proposal())
    try:
        result.level = "weak"  # type: ignore
        raise AssertionError("assessment must be frozen")
    except dataclasses.FrozenInstanceError:
        pass


def test_malformed_rejected():
    guard = DefaultConfidenceGuard()
    for bad in ("nope", None):
        try:
            guard.assess(bad, _proposal())  # type: ignore
            raise AssertionError("expected TypeError")
        except TypeError:
            pass
        try:
            guard.assess(_unit(), bad)  # type: ignore
            raise AssertionError("expected TypeError")
        except TypeError:
            pass


def test_registry_behaviour():
    registry = ConfidenceGuardRegistry()
    assert isinstance(registry.default(), EvidenceStrengthGuard)
    registry.register("extra", EvidenceStrengthGuard(strategy="extra"))
    assert registry.get("extra").name == "extra"
    try:
        registry.register("extra", DefaultConfidenceGuard())
        raise AssertionError("expected duplicate error")
    except ValueError:
        pass
    try:
        registry.get("missing")
        raise AssertionError("expected unknown error")
    except ValueError:
        pass
