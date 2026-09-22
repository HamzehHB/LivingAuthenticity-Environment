"""Controlled-execution result value object (inspectable, no authority).

An ExecutionResult reports what happened for one explicitly authorized
proposal. It never authorizes further action.
"""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ExecutionResult:
    """Inspectable outcome of one controlled execution attempt."""

    attempted: bool = False
    permitted: bool = False
    executed: bool = False
    proposal_hash: str = ""
    action: str = ""
    destination: str = ""
    artifact_path: str = ""
    reason: str = ""
    failed_check: str = ""
    revalidation_valid: bool = False
    provenance: tuple = field(default_factory=tuple)
    is_authoritative: bool = False
    requires_human_review: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "attempted", bool(self.attempted))
        object.__setattr__(self, "permitted", bool(self.permitted))
        object.__setattr__(self, "executed", bool(self.executed))
        object.__setattr__(self, "revalidation_valid", bool(self.revalidation_valid))
        object.__setattr__(self, "is_authoritative", False)
        object.__setattr__(self, "requires_human_review", True)
