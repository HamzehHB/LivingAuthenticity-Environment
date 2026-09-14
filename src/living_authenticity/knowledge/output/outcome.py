"""Immutable generated-note value object for the output stage.

A GeneratedNote is a proposed Obsidian Markdown representation of an
already-built analytical Proposal. It is staging/proposal-oriented
data only: non-authoritative, requiring human review, with its
proposed destination stored as inert metadata.
"""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class GeneratedNote:
    """Proposed note representation; never an authoritative note."""

    query_unit_id: str
    query_source: str
    query_position: int
    title: str = ""
    body: str = ""
    proposed_type: str = ""
    proposal_action: str = "NEEDS_REVIEW"
    confidence_level: str = ""
    destination: str = ""
    frontmatter: tuple = field(default_factory=tuple)
    evidence: tuple = field(default_factory=tuple)
    uncertainties: tuple = field(default_factory=tuple)
    provenance: tuple = field(default_factory=tuple)
    markdown: str = ""
    strategy: str = ""
    note: str = ""
    is_authoritative: bool = False
    requires_human_review: bool = True

    def __post_init__(self) -> None:
        """Fix authority flags: generation never authorizes."""
        object.__setattr__(self, "is_authoritative", False)
        object.__setattr__(self, "requires_human_review", True)
