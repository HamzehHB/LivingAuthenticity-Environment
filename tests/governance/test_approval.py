"""Explicit approval tests: seven human-authority invariants."""
import dataclasses

import pytest

from src.living_authenticity.knowledge.governance.approval import (
    ApprovalGateRegistry,
    ApprovalOutcome,
    ExplicitApprovalGate,
    audit_record,
    canonical_proposal_hash,
    parse_approval_input,
    proposal_payload,
    revalidate,
)
from src.living_authenticity.knowledge.decision.confidence.outcome import ConfidenceAssessment
from src.living_authenticity.knowledge.ingestion.extraction.knowledge_unit import KnowledgeUnit
from src.living_authenticity.knowledge.decision.proposal.builder import ProposalBuilder


def _unit(uid="q1", text="A calm morning observation about attention"):
    return KnowledgeUnit(
        id=uid, source="inbox", original_text=text,
        meaning=text, cleaned_text=text, normalized_text=text,
        context="", proposed_type="", position=1,
    )


def _proposal(unit=None, dest="Staging/note.md"):
    return ProposalBuilder().build(unit or _unit(), destination=dest)


def _conf():
    return ConfidenceAssessment(
        query_unit_id="q1", query_source="inbox", query_position=1,
        proposal_action="NEEDS_REVIEW", level="weak", strategy="s",
        basis="b", uncertainties=("gap",),
    )


def _request(text="alpha text about attention"):
    gate = ExplicitApprovalGate()
    return gate.build_request(_unit(text=text), _proposal(_unit(text=text)), _conf())


def test_1_explicit_only_deliberate_input_approves():
    gate = ExplicitApprovalGate()
    query, proposal = _unit(), _proposal()
    request, text, outcome = gate.request_approval(
        query, proposal, _conf(), reader=lambda: "yes")
    assert outcome.approved is True
    for raw in ("", "n", "no", "maybe", "yep", "1", "ok", "approve"):
        req, _, out = gate.request_approval(
            query, proposal, _conf(), reader=lambda r=raw: r)
        assert out.approved is False, raw
    def _boom():
        raise EOFError("no input")
    _, _, out = gate.request_approval(query, proposal, _conf(), reader=_boom)
    assert out.approved is False
    assert "Proposed Action:" in text and "Approve this action? [y/N]:" in text
    assert "Confidence:" in text


def test_2_specific_bound_to_exact_proposal_hash():
    gate = ExplicitApprovalGate()
    query = _unit(text="alpha text about attention")
    proposal = _proposal(_unit(text="alpha text about attention"))
    request = gate.build_request(query, proposal, _conf())
    assert request.proposal_hash == canonical_proposal_hash(
        proposal_payload(proposal, _conf()))
    other = _proposal(_unit(text="beta text about attention"))
    assert other.title != proposal.title
    assert gate.build_request(query, other, _conf()).proposal_hash != request.proposal_hash
    outcome = gate.decide(request, "y", timestamp="2026-01-01T00:00:00+00:00")
    ok, _ = revalidate(request, outcome, other, _conf())
    assert ok is False


def test_3_non_batch_one_proposal_at_a_time():
    gate = ExplicitApprovalGate()
    first = gate.build_request(_unit("q1"), _proposal(_unit("q1")))
    second = gate.build_request(_unit("q2"), _proposal(_unit("q2")))
    assert first.proposal_hash != second.proposal_hash
    out = gate.decide(first, "y", timestamp="t")
    ok_other, _ = revalidate(second, out)
    assert ok_other is False
    assert not hasattr(gate, "approve_all")
    assert not hasattr(gate, "approve_remaining")


def test_4_non_standing_no_reuse_for_future_proposal():
    gate = ExplicitApprovalGate()
    query = _unit()
    first = gate.build_request(query, _proposal())
    out = gate.decide(first, "yes", timestamp="t")
    second = gate.build_request(query, _proposal())
    assert second.proposal_hash == first.proposal_hash
    assert out.proposal_hash == second.proposal_hash
    fresh = gate.decide(second, "", timestamp="t2")
    assert fresh.approved is False
    assert not hasattr(gate, "standing_approval")


def test_5_non_transferable_rejected_for_different_proposal():
    gate = ExplicitApprovalGate()
    req_a = _request("alpha text about attention")
    req_b = _request("alpha text about attention!")
    assert req_a.proposal_hash != req_b.proposal_hash
    out_a = gate.decide(req_a, "y", timestamp="t")
    ok, reason = revalidate(req_b, out_a)
    assert ok is False
    assert "different proposal" in reason

def test_6_accepted_values_only_default_reject():
    assert parse_approval_input("y") is True
    assert parse_approval_input("yes") is True
    assert parse_approval_input(" Y ") is True
    assert parse_approval_input("YES") is True
    for raw in ("", " ", "n", "N", "no", "NO", "yess", "yy", "1",
                "true", "ok", "approve", "approved", "[y/N]"):
        assert parse_approval_input(raw) is False, repr(raw)
    with pytest.raises(TypeError):
        parse_approval_input(None)  # type: ignore
    with pytest.raises(TypeError):
        parse_approval_input(1)  # type: ignore
    with pytest.raises(TypeError):
        parse_approval_input(["y"])  # type: ignore


def test_7_no_fabricated_approval_under_any_circumstance():
    gate = ExplicitApprovalGate()
    query, proposal = _unit(), _proposal()
    with pytest.raises(TypeError):
        gate.request_approval(query, proposal, _conf(), reader="not-callable")  # type: ignore
    def _timeout():
        raise TimeoutError("timed out")
    _, _, out = gate.request_approval(query, proposal, _conf(), reader=_timeout)
    assert out.approved is False
    bare = ApprovalOutcome(query_unit_id="q1", proposal_hash="h")
    assert bare.approved is False
    assert bare.is_authoritative is False
    assert bare.requires_human_review is True
    with pytest.raises(TypeError):
        gate.decide(_request(), None)  # type: ignore


def test_display_shows_required_proposal_fields():
    request = _request()
    text = ExplicitApprovalGate().display(request)
    for marker in ("Proposed Action:", "Title:", "Destination:", "Reason:",
                   "Confidence:", "Approve this action? [y/N]:"):
        assert marker in text


def test_revalidation_detects_changed_proposal_and_scope():
    gate = ExplicitApprovalGate()
    query = _unit(text="alpha text about attention")
    proposal = _proposal(_unit(text="alpha text about attention"))
    request = gate.build_request(query, proposal, _conf())
    outcome = gate.decide(request, "y", timestamp="t")
    ok, _ = revalidate(request, outcome, proposal, _conf())
    assert ok is True
    changed = _proposal(_unit(text="alpha text about attention"), dest="Other/place.md")
    ok2, reason2 = revalidate(request, outcome, changed, _conf())
    assert ok2 is False
    assert "changed" in reason2
    rejected = gate.decide(request, "n", timestamp="t")
    ok3, _ = revalidate(request, rejected, proposal, _conf())
    assert ok3 is False
def test_audit_record_minimum_fields():
    request = _request()
    outcome = ExplicitApprovalGate().decide(request, "yes", timestamp="2026-01-01T00:00:00+00:00")
    record = audit_record(request, outcome, True)
    assert record["proposed_action"] == request.proposal_action
    assert record["approval_status"] == "approved"
    assert record["timestamp"] == "2026-01-01T00:00:00+00:00"
    assert record["proposal_reference"] == request.proposal_hash
    assert record["provenance_reference"] == "q1"
    assert record["execution_result"] == "not_executed"
    record2 = audit_record(request, ExplicitApprovalGate().decide(request, "n", timestamp="t"), False)
    assert record2["approval_status"] == "rejected"
    assert record2["revalidation"] == "failed"


def test_outcomes_immutable_and_non_authoritative():
    request = _request()
    outcome = ExplicitApprovalGate().decide(request, "y", timestamp="t")
    assert request.is_authoritative is False
    assert request.requires_human_review is True
    assert outcome.is_authoritative is False
    assert outcome.requires_human_review is True
    with pytest.raises(dataclasses.FrozenInstanceError):
        request.title = "x"  # type: ignore
    with pytest.raises(dataclasses.FrozenInstanceError):
        outcome.approved = False  # type: ignore


def test_registry_and_hash_determinism():
    reg = ApprovalGateRegistry()
    assert isinstance(reg.default(), ExplicitApprovalGate)
    reg.register("extra", ExplicitApprovalGate(strategy="extra"))
    assert reg.get("extra").name == "extra"
    with pytest.raises(ValueError):
        reg.register("extra", ExplicitApprovalGate())
    with pytest.raises(ValueError):
        reg.get("missing")
    payload = proposal_payload(_proposal())
    assert canonical_proposal_hash(payload) == canonical_proposal_hash(dict(payload))
    with pytest.raises(TypeError):
        canonical_proposal_hash("nope")  # type: ignore
    with pytest.raises(TypeError):
        proposal_payload("nope")  # type: ignore


def test_malformed_inputs_rejected():
    gate = ExplicitApprovalGate()
    with pytest.raises(TypeError):
        gate.build_request("nope", _proposal())  # type: ignore
    with pytest.raises(TypeError):
        gate.build_request(_unit(), "nope")  # type: ignore
    with pytest.raises(ValueError):
        gate.build_request(_unit("other"), _proposal(_unit("q1")))
    with pytest.raises(TypeError):
        gate.display("nope")  # type: ignore
    with pytest.raises(TypeError):
        gate.decide("nope", "y")  # type: ignore
    with pytest.raises(TypeError):
        revalidate("nope", ApprovalOutcome(query_unit_id="q", proposal_hash="h"))  # type: ignore

