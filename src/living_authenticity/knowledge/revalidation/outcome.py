"""Revalidation result value object (no execution)."""
from dataclasses import dataclass, field

REVALIDATION_CHECKS = (
    "proposal_identity",
    "proposal_contents",
    "target",
    "destination",
    "relevant_data",
    "action_eligibility",
    "provenance",
    "schema_state",
    "approval_binding",
)


@dataclass(frozen=True)
class RevalidationResult:
    """Deterministic outcome of revalidating one approved proposal.

    ``valid`` is True only when every performed check passed. A valid
    result means the exact approved proposal remains eligible for the
    later controlled-execution boundary; it never authorizes execution.
    """

    valid: bool = False
    failed_check: str = ""
    reason: str = ""
    checks: tuple = field(default_factory=lambda: REVALIDATION_CHECKS)
    approval_bound: bool = False
    eligible: bool = False
    is_authoritative: bool = False
    requires_human_review: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "valid", bool(self.valid))
        object.__setattr__(self, "approval_bound", bool(self.approval_bound))
        object.__setattr__(self, "eligible", bool(self.eligible))
        object.__setattr__(self, "is_authoritative", False)
        object.__setattr__(self, "requires_human_review", True)
