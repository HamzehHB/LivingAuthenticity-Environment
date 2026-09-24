"""Analytical knowledge-filter outcome value object."""
from dataclasses import dataclass, field
FILTER_VERDICTS = ("pass_to_review", "hold_for_review", "do_not_import")


@dataclass(frozen=True)
class FilterOutcome:
    """Non-authoritative analytical boundary signal for one query unit."""
    query_unit_id: str
    query_source: str
    query_position: int
    verdict: str = "hold_for_review"
    recommended_action: str = "NEEDS_REVIEW"
    basis: str = ""
    uncertainties: tuple = field(default_factory=tuple)
    evidence: tuple = field(default_factory=tuple)
    strategy: str = ""
    note: str = ""
    is_authoritative: bool = False
    requires_human_review: bool = True

    def __post_init__(self) -> None:
        if self.verdict not in FILTER_VERDICTS:
            object.__setattr__(self, "verdict", "hold_for_review")
        from src.living_authenticity.knowledge.decision.proposal.outcome import PROPOSAL_ACTIONS
        if self.recommended_action not in PROPOSAL_ACTIONS:
            object.__setattr__(self, "recommended_action", "NEEDS_REVIEW")
        object.__setattr__(self, "is_authoritative", False)
        object.__setattr__(self, "requires_human_review", True)
