"""Analytical Core analysis result value object."""

from dataclasses import dataclass, field


# Minimal explicitly non-authoritative vocabulary for this analytical stage.
# Token overlap alone can only justify "potentially_relevant" or weaker
# observations; stronger claims (supports/challenges/conflict) require
# semantic evidence this analyzer does not possess.
CORE_RELEVANCE_VALUES = (
    "potentially_relevant",
    "no_observed_relevance",
    "insufficient_evidence",
)


@dataclass(frozen=True)
class CoreAnalysisResult:
    """Evidence-only Core relevance observation for one query unit.

    ``is_authoritative`` is always ``False``: analytical output is never
    authoritative Core knowledge. ``requires_human_review`` is ``True``
    whenever the observation could inform a consequential decision, so the
    human reviewer stays in control.
    """

    query_unit_id: str
    query_source: str
    query_position: int
    strategy: str = ""
    relevance: str = "insufficient_evidence"
    basis: str = ""
    shared_terms: tuple = ()
    examined_core_ids: tuple = ()
    note: str = ""
    is_authoritative: bool = False
    requires_human_review: bool = True
    evidence: tuple = field(default_factory=tuple)

    @property
    def is_potentially_relevant(self) -> bool:
        """True only for the conservative potentially_relevant observation."""
        return self.relevance == "potentially_relevant"
