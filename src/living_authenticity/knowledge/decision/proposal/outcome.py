"""Immutable proposal representation for the analytical proposal stage.

A proposal is a non-authoritative analytical recommendation awaiting
human review. It is not approval, authorization, execution, or
persistence, and it never modifies authoritative knowledge.
"""

from dataclasses import dataclass, field

# Executable proposal actions in the current scope. Any other action is
# unsupported and must resolve conservatively to NEEDS_REVIEW.
PROPOSAL_ACTIONS = (
    "CREATE",
    "DO_NOT_IMPORT",
    "NEEDS_REVIEW",
)


@dataclass(frozen=True)
class Proposal:
    """Structured, traceable, non-authoritative proposal for human review.

    All untrusted content (titles, destinations, evidence strings) is
    stored as inert data only and must never be interpreted as
    instructions or executable operations.
    """

    query_unit_id: str
    query_source: str
    query_position: int
    action: str = "NEEDS_REVIEW"
    title: str = ""
    destination: str = ""
    reason: str = ""
    evidence: tuple = field(default_factory=tuple)
    relevant_candidates: tuple = field(default_factory=tuple)
    uncertainties: tuple = field(default_factory=tuple)
    provenance: tuple = field(default_factory=tuple)
    classification_type: str = ""
    comparison_summary: str = ""
    relation_summary: str = ""
    core_relevance: str = ""
    strategy: str = ""
    note: str = ""
    is_authoritative: bool = False
    requires_human_review: bool = True

    @property
    def is_supported_action(self) -> bool:
        """True only for the executable action vocabulary."""
        return self.action in PROPOSAL_ACTIONS

    def __post_init__(self) -> None:
        """Enforce conservative invariants on direct construction.

        The builder only emits supported actions with fixed authority
        flags, but direct construction must also be conservative:
        an unsupported action coerces to NEEDS_REVIEW, and the
        non-authoritative / human-review flags are fixed because a
        proposal is never approval, authorization, or execution.
        Frozen dataclass, so bypass via object.
        """
        if self.action not in PROPOSAL_ACTIONS:
            object.__setattr__(self, "action", "NEEDS_REVIEW")
        object.__setattr__(self, "is_authoritative", False)
        object.__setattr__(self, "requires_human_review", True)
