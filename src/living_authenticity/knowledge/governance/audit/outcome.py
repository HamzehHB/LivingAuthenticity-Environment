"""Audit / traceability record (observational only).

Builds a frozen, deterministic, in-memory record linking one proposal
identity to its human approval, fresh revalidation result, and
controlled-execution outcome. The record never authorizes, executes,
or mutates knowledge: it only copies fields that already exist on the
supplied contracts.
"""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class AuditRecord:
    """Inspectable trace of one proposal lifecycle attempt."""

    proposal_hash: str = ""
    query_unit_id: str = ""
    query_source: str = ""
    query_position: int = 0
    proposal_action: str = ""
    approval_approved: bool = False
    approval_proposal_hash: str = ""
    approval_query_unit_id: str = ""
    approval_timestamp: str = ""
    approval_strategy: str = ""
    revalidation_performed: bool = False
    revalidation_valid: bool = False
    revalidation_failed_check: str = ""
    revalidation_reason: str = ""
    execution_attempted: bool = False
    execution_permitted: bool = False
    execution_executed: bool = False
    execution_proposal_hash: str = ""
    execution_reason: str = ""
    execution_failed_check: str = ""
    artifact_reference: str = ""
    destination: str = ""
    provenance: tuple = field(default_factory=tuple)
    is_authoritative: bool = False
    requires_human_review: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "approval_approved", bool(self.approval_approved))
        object.__setattr__(self, "revalidation_performed", bool(self.revalidation_performed))
        object.__setattr__(self, "revalidation_valid", bool(self.revalidation_valid))
        object.__setattr__(self, "execution_attempted", bool(self.execution_attempted))
        object.__setattr__(self, "execution_permitted", bool(self.execution_permitted))
        object.__setattr__(self, "execution_executed", bool(self.execution_executed))
        object.__setattr__(self, "provenance", tuple(self.provenance))
        object.__setattr__(self, "is_authoritative", False)
        object.__setattr__(self, "requires_human_review", True)

    @property
    def identity_consistent(self) -> bool:
        """True when all present stage identities agree with the proposal.

        Missing stages (``None`` at build time) are not inconsistencies:
        only identities actually recorded are compared. A ``False`` value
        is itself the traceable inconsistency signal; it never blocks,
        repairs, or authorizes anything.
        """
        if self.approval_proposal_hash and (
            self.approval_proposal_hash != self.proposal_hash
        ):
            return False
        if self.approval_query_unit_id and (
            self.approval_query_unit_id != self.query_unit_id
        ):
            return False
        if self.execution_proposal_hash and (
            self.execution_proposal_hash != self.proposal_hash
        ):
            return False
        return True

    @property
    def outcome(self) -> str:
        """Human-readable lifecycle state derived from stored flags."""
        if self.execution_executed:
            return "executed"
        if self.execution_attempted:
            return "rejected"
        if self.revalidation_performed and not self.revalidation_valid:
            return "revalidation_failed"
        if not self.approval_approved:
            return "not_approved"
        return "not_executed"


def build_audit_record(request, outcome, revalidation=None, execution=None,
                       proposal=None) -> AuditRecord:
    """Build one AuditRecord from existing lifecycle contracts.

    ``request`` (ApprovalRequest) and ``outcome`` (ApprovalOutcome) are
    required. ``revalidation`` (RevalidationResult), ``execution``
    (ExecutionResult), and ``proposal`` (Proposal) are optional: ``None``
    means that stage/object was not supplied, which the record preserves
    faithfully instead of inventing a result. Provenance prefers the
    execution record when present and otherwise preserves the supplied
    proposal provenance without inventing any entry. No filesystem,
    network, or knowledge-store side effects.
    """
    from src.living_authenticity.knowledge.governance.approval.outcome import (
        ApprovalOutcome,
        ApprovalRequest,
    )

    if not isinstance(request, ApprovalRequest):
        raise TypeError("request must be an ApprovalRequest")
    if not isinstance(outcome, ApprovalOutcome):
        raise TypeError("outcome must be an ApprovalOutcome")
    if revalidation is not None:
        from src.living_authenticity.knowledge.governance.revalidation.outcome import (
            RevalidationResult,
        )

        if not isinstance(revalidation, RevalidationResult):
            raise TypeError("revalidation must be a RevalidationResult")
    if execution is not None:
        from src.living_authenticity.knowledge.governance.execution.outcome import (
            ExecutionResult,
        )

        if not isinstance(execution, ExecutionResult):
            raise TypeError("execution must be an ExecutionResult")
    if proposal is not None:
        from src.living_authenticity.knowledge.decision.proposal.outcome import Proposal

        if not isinstance(proposal, Proposal):
            raise TypeError("proposal must be a Proposal")
    provenance = ()
    if execution is not None:
        provenance = tuple(execution.provenance)
    elif proposal is not None:
        provenance = tuple(proposal.provenance)
    return AuditRecord(
        proposal_hash=request.proposal_hash,
        query_unit_id=request.query_unit_id,
        query_source=request.query_source,
        query_position=request.query_position,
        proposal_action=request.proposal_action,
        approval_approved=bool(outcome.approved),
        approval_proposal_hash=outcome.proposal_hash,
        approval_query_unit_id=outcome.query_unit_id,
        approval_timestamp=outcome.timestamp,
        approval_strategy=outcome.strategy,
        revalidation_performed=revalidation is not None,
        revalidation_valid=bool(revalidation.valid) if revalidation is not None else False,
        revalidation_failed_check=revalidation.failed_check if revalidation is not None else "",
        revalidation_reason=revalidation.reason if revalidation is not None else "",
        execution_attempted=bool(execution.attempted) if execution is not None else False,
        execution_permitted=bool(execution.permitted) if execution is not None else False,
        execution_executed=bool(execution.executed) if execution is not None else False,
        execution_proposal_hash=execution.proposal_hash if execution is not None else "",
        execution_reason=execution.reason if execution is not None else "",
        execution_failed_check=execution.failed_check if execution is not None else "",
        artifact_reference=execution.artifact_path if execution is not None else "",
        destination=execution.destination if execution is not None else request.destination,
        provenance=provenance,
    )


def record_audit_for_execution(request, outcome, revalidation, execution,
                               proposal=None) -> AuditRecord:
    """Record the audit trace for one completed controlled-execution attempt.

    Minimal deterministic connection from the existing controlled flow to
    the observational audit record: the caller passes the exact objects
    already produced by approval, fresh revalidation, and
    ``ControlledExecutor``. This function executes nothing, writes
    nothing, and authorizes nothing; it only forwards the supplied
    contracts to :func:`build_audit_record`.
    """
    return build_audit_record(request, outcome, revalidation, execution, proposal)
