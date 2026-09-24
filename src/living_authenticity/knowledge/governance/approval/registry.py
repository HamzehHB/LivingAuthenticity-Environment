"""Approval registries and revalidation."""
from src.living_authenticity.knowledge.decision.proposal.outcome import PROPOSAL_ACTIONS

from .explicit_gate import ExplicitApprovalGate
from .outcome import ApprovalOutcome, ApprovalRequest
from .proposal_hash import canonical_proposal_hash, proposal_payload


class ApprovalGateRegistry:
    """Registry of approval gates."""

    def __init__(self) -> None:
        self._gates = {"explicit_cli": ExplicitApprovalGate(strategy="explicit_cli")}

    def default(self) -> ExplicitApprovalGate:
        return self._gates["explicit_cli"]

    def register(self, name: str, gate) -> None:
        if not isinstance(name, str) or not name:
            raise TypeError("name must be a non-empty string")
        if not isinstance(gate, ExplicitApprovalGate):
            raise TypeError("gate must be an ExplicitApprovalGate")
        if name in self._gates:
            raise ValueError("duplicate gate: " + name)
        self._gates[name] = gate

    def get(self, name: str):
        try:
            return self._gates[name]
        except KeyError:
            raise ValueError("unknown gate: " + str(name)) from None


def revalidate(request, outcome, proposal=None, confidence=None) -> tuple:
    """Revalidate an approval before any future execution step.

    Returns (ok, reason). ok is True only when the outcome is an
    explicit approval bound to this exact request and the live proposal
    still hashes identically. No execution is performed here.
    """
    if not isinstance(request, ApprovalRequest):
        raise TypeError("request must be an ApprovalRequest")
    if not isinstance(outcome, ApprovalOutcome):
        raise TypeError("outcome must be an ApprovalOutcome")
    if outcome.proposal_hash != request.proposal_hash:
        return (False, "approval bound to a different proposal")
    if outcome.query_unit_id != request.query_unit_id:
        return (False, "approval bound to a different query unit")
    if not outcome.approved:
        return (False, "proposal was not approved")
    if request.proposal_action not in PROPOSAL_ACTIONS:
        return (False, "action outside executable scope")
    if proposal is not None:
        live = proposal_payload(proposal, confidence)
        if canonical_proposal_hash(live) != request.proposal_hash:
            return (False, "proposal changed after approval")
    return (True, "revalidated: exact proposal unchanged")


def audit_record(request, outcome, revalidation_ok: bool, execution_result: str = "not_executed") -> dict:
    """Build the audit record for one approval decision."""
    if not isinstance(request, ApprovalRequest):
        raise TypeError("request must be an ApprovalRequest")
    if not isinstance(outcome, ApprovalOutcome):
        raise TypeError("outcome must be an ApprovalOutcome")
    return {
        "proposed_action": request.proposal_action,
        "approval_status": ("approved" if outcome.approved else "rejected"),
        "timestamp": outcome.timestamp,
        "proposal_reference": outcome.proposal_hash,
        "provenance_reference": request.query_unit_id,
        "revalidation": ("passed" if revalidation_ok else "failed"),
        "execution_result": execution_result,
    }
