"""Revalidation tests: validation boundary, no execution."""
import dataclasses
import pytest
from src.living_authenticity.knowledge.approval.explicit_gate import ExplicitApprovalGate
from src.living_authenticity.knowledge.approval.outcome import ApprovalRequest
from src.living_authenticity.knowledge.confidence.outcome import ConfidenceAssessment
from src.living_authenticity.knowledge.extraction.knowledge_unit import KnowledgeUnit
from src.living_authenticity.knowledge.proposal.builder import ProposalBuilder
from src.living_authenticity.knowledge.proposal.outcome import Proposal
from src.living_authenticity.knowledge.revalidation import (
    REVALIDATION_CHECKS, RevalidationResult, Revalidator, revalidate_proposal)


def _unit(uid="q1", text="A calm morning observation about attention"):
    return KnowledgeUnit(id=uid, source="inbox", original_text=text,
        meaning=text, cleaned_text=text, normalized_text=text,
        context="", proposed_type="", position=1)


def _proposal(unit=None, dest="Staging/note.md"):
    return ProposalBuilder().build(unit or _unit(), destination=dest)


def _conf(action="NEEDS_REVIEW"):
    return ConfidenceAssessment(query_unit_id="q1", query_source="inbox",
        query_position=1, proposal_action=action, level="weak",
        strategy="s", basis="b", uncertainties=("gap",))


def _approved(dest="Staging/note.md"):
    gate = ExplicitApprovalGate()
    query = _unit()
    proposal = _proposal(_unit(), dest=dest)
    conf = _conf(proposal.action)
    request = gate.build_request(query, proposal, conf)
    outcome = gate.decide(request, "yes", timestamp="2026-01-01T00:00:00+00:00")
    return gate, query, proposal, conf, request, outcome


def test_valid_approved_proposal_revalidates():
    _, _, proposal, conf, request, outcome = _approved()
    result = revalidate_proposal(request, outcome, proposal, conf)
    assert result.valid is True
    assert result.approval_bound is True and result.eligible is True
    assert result.failed_check == ""
    assert result.checks == REVALIDATION_CHECKS
    assert result.is_authoritative is False
    assert result.requires_human_review is True


def test_proposal_identity_mismatch_fails():
    _, _, proposal, conf, request, outcome = _approved()
    other = _proposal(_unit(text="A different evening note about focus"))
    result = revalidate_proposal(request, outcome, other, conf)
    assert result.valid is False and result.failed_check != ""


def test_proposal_contents_change_fails():
    _, _, proposal, conf, request, outcome = _approved()
    changed = dataclasses.replace(proposal, reason="changed reason text")
    result = revalidate_proposal(request, outcome, changed, conf)
    assert result.valid is False
    assert result.failed_check in ("proposal_contents", "proposal_identity")


def test_target_change_fails():
    _, _, proposal, conf, request, outcome = _approved()
    changed = dataclasses.replace(proposal, query_unit_id="q2")
    result = revalidate_proposal(request, outcome, changed, conf)
    assert result.valid is False and result.failed_check == "target"


def test_destination_change_fails():
    _, _, proposal, conf, request, outcome = _approved()
    changed = _proposal(_unit(), dest="Other/place.md")
    result = revalidate_proposal(request, outcome, changed, conf)
    assert result.valid is False and result.failed_check == "destination"


def test_evidence_change_fails():
    _, _, proposal, conf, request, outcome = _approved()
    other_conf = ConfidenceAssessment(query_unit_id="q1", query_source="inbox",
        query_position=1, proposal_action=proposal.action,
        level="sufficiently_supported", strategy="s", basis="b",
        uncertainties=())
    result = revalidate_proposal(request, outcome, proposal, other_conf)
    assert result.valid is False and result.failed_check == "relevant_data"


def test_unsupported_action_fails():
    gate = ExplicitApprovalGate()
    _, _, proposal, conf, request, outcome = _approved()
    bad_request = dataclasses.replace(request, proposal_action="MERGE")
    bad_outcome = gate.decide(bad_request, "yes", timestamp="t")
    result = revalidate_proposal(bad_request, bad_outcome, proposal, conf)
    assert result.valid is False and result.failed_check == "action_eligibility"
    direct = Proposal(query_unit_id="q1", query_source="inbox", query_position=1,
        action="UPDATE", title="t", destination="Staging/note.md")
    assert direct.action == "NEEDS_REVIEW"


def test_provenance_mismatch_fails():
    _, _, proposal, conf, request, outcome = _approved()
    changed = dataclasses.replace(proposal, provenance=("query:other@inbox#1",))
    gate = ExplicitApprovalGate()
    req2 = gate.build_request(_unit(), changed, conf)
    out2 = gate.decide(req2, "yes", timestamp="t")
    result = revalidate_proposal(req2, out2, changed, conf)
    assert result.valid is False and result.failed_check == "provenance"


def test_schema_state_incompatibility_fails():
    _, _, proposal, conf, request, outcome = _approved()
    result = revalidate_proposal(request, outcome, proposal, conf, schema_version="9.9.9")
    assert result.valid is False and result.failed_check == "schema_state"
def test_schema_state_valid_and_empty_pass_through():
    _, _, proposal, conf, request, outcome = _approved()
    ok_default = revalidate_proposal(request, outcome, proposal, conf)
    assert ok_default.valid is True
    ok_empty = revalidate_proposal(request, outcome, proposal, conf, schema_version="")
    assert ok_empty.valid is True
    ok_pinned = revalidate_proposal(request, outcome, proposal, conf, schema_version="1.0.0")
    assert ok_pinned.valid is True
    with pytest.raises(TypeError):
        revalidate_proposal(request, outcome, proposal, conf, schema_version=123)  # type: ignore[arg-type]


def test_provenance_missing_fails():
    _, _, proposal, conf, request, outcome = _approved()
    changed = dataclasses.replace(proposal, provenance=())
    gate = ExplicitApprovalGate()
    req2 = gate.build_request(_unit(), changed, conf)
    out2 = gate.decide(req2, "yes", timestamp="t")
    result = revalidate_proposal(req2, out2, changed, conf)
    assert result.valid is False and result.failed_check == "provenance"


def test_missing_live_proposal_fails():
    _, _, proposal, conf, request, outcome = _approved()
    result = revalidate_proposal(request, outcome, None, conf)
    assert result.valid is False and result.failed_check == "proposal_identity"




def test_approval_binding_mismatch_fails():
    gate, query, proposal, conf, request, outcome = _approved()
    other = _proposal(_unit(text="A different evening note about focus"))
    other_req = gate.build_request(query, other, conf)
    result = revalidate_proposal(other_req, outcome, other, conf)
    assert result.valid is False and result.failed_check == "approval_binding"


def test_unapproved_cannot_pass():
    gate, query, proposal, conf, request, _ = _approved()
    rejected = gate.decide(request, "n", timestamp="t")
    result = revalidate_proposal(request, rejected, proposal, conf)
    assert result.valid is False


def test_approval_from_another_proposal_cannot_transfer():
    gate = ExplicitApprovalGate()
    _, _, _, _, req_a, out_a = _approved()
    proposal_b = _proposal(_unit(text="A different evening note about focus"))
    conf_b = _conf(proposal_b.action)
    req_b = gate.build_request(_unit(text="A different evening note about focus"),
        proposal_b, conf_b)
    result = revalidate_proposal(req_b, out_a, proposal_b, conf_b)
    assert result.valid is False


def test_no_batch_and_no_standing():
    validator = Revalidator()
    assert not hasattr(validator, "revalidate_all")
    assert not hasattr(validator, "approve_all")
    assert not hasattr(validator, "standing_approval")
    import inspect
    params = list(inspect.signature(validator.revalidate).parameters)
    assert params[:3] == ["request", "outcome", "proposal"]


def test_no_execution_or_filesystem_effects():
    import pathlib
    import src.living_authenticity.knowledge.revalidation.revalidator as mod
    source = pathlib.Path(mod.__file__).read_text(encoding="utf-8")
    for bad in ("open(", "write_text", "mkdir", "shutil", "os.system",
                "exec(", "eval(", "pickle", "__import__"):
        assert bad not in source
    _, _, proposal, conf, request, outcome = _approved()
    result = revalidate_proposal(request, outcome, proposal, conf)
    assert result.valid is True
    payload = dataclasses.asdict(result)
    for bad in ("execute", "write", "commit", "apply", "authorized"):
        assert bad not in payload


def test_failure_deterministic_and_inspectable():
    _, _, proposal, conf, request, outcome = _approved()
    changed = _proposal(_unit(), dest="Other/place.md")
    first = revalidate_proposal(request, outcome, changed, conf)
    second = revalidate_proposal(request, outcome, changed, conf)
    assert first == second
    assert first.valid is False and first.reason


def test_malformed_inputs_rejected():
    _, _, proposal, conf, request, outcome = _approved()
    with pytest.raises(TypeError):
        revalidate_proposal("nope", outcome, proposal, conf)
    with pytest.raises(TypeError):
        revalidate_proposal(request, "nope", proposal, conf)
    with pytest.raises(TypeError):
        revalidate_proposal(request, outcome, "nope", conf)
    with pytest.raises(TypeError):
        revalidate_proposal(request, outcome, proposal, "nope")


def test_security_substitution_attempts():
    _, _, proposal, conf, request, outcome = _approved()
    for dest in ("../../vault/secret.md", "/etc/passwd", "Staging/../vault.md"):
        changed = dataclasses.replace(proposal, destination=dest)
        result = revalidate_proposal(request, outcome, changed, conf)
        assert result.valid is False
    tampered = dataclasses.replace(proposal, provenance=("query:fabricated@vault#9",))
    gate = ExplicitApprovalGate()
    req2 = gate.build_request(_unit(), tampered, conf)
    out2 = gate.decide(req2, "yes", timestamp="t")
    assert revalidate_proposal(req2, out2, tampered, conf).valid is False
    stale = dataclasses.replace(proposal, title="stale title")
    assert revalidate_proposal(request, outcome, stale, conf).valid is False


def test_human_approval_not_fabricated_by_validation():
    validator = Revalidator()
    assert not hasattr(validator, "approve")
    assert not hasattr(validator, "decide")
    _, _, proposal, conf, request, outcome = _approved()
    assert outcome.approved is True
    result = revalidate_proposal(request, outcome, proposal, conf)
    assert isinstance(result, RevalidationResult)
    assert not isinstance(result, ApprovalRequest)
