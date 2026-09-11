"""Analytical relation detection result value objects."""

from dataclasses import dataclass

# Minimal explicitly non-authoritative vocabulary for this analytical stage.
# Only lexical/topical relatedness (or its explicit absence) can be
# established by token-overlap evidence. All other canonical relation types
# (supports, challenges, extends, ...) require semantic evidence this
# detector does not possess, so they are deliberately not emitted.
PROPOSED_RELATIONS = (
    "related",
    "no_proposed_relation",
    "unresolved",
)


@dataclass(frozen=True)
class ProposedRelation:
    """One proposed analytical relationship between two actual units."""

    candidate_unit_id: str
    candidate_source: str
    candidate_position: int
    relation: str = "unresolved"
    basis: str = ""
    shared_terms: tuple = ()
    comparison_category: str = ""

    def __post_init__(self) -> None:
        """Coerce unsupported relations to unresolved.

        Builders only emit supported relation values, but direct
        construction must also be conservative: an unknown relation
        can never survive as an accepted analytical signal.
        """
        if self.relation not in PROPOSED_RELATIONS:
            object.__setattr__(self, "relation", "unresolved")


@dataclass(frozen=True)
class RelationDetectionResult:
    """Evidence-only relation detection outcome for one query unit."""

    query_unit_id: str
    query_source: str
    query_position: int
    strategy: str = ""
    proposals: tuple = ()
    note: str = ""

    @property
    def has_proposals(self) -> bool:
        """True when at least one related proposal was detected."""
        return any(p.relation == "related" for p in self.proposals)
