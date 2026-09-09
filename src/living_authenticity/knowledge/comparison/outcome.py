"""Analytical comparison result value object."""

from dataclasses import dataclass

COMPARISON_CATEGORIES = (
    "identical_content",
    "possible_duplicate",
    "related_but_distinct",
    "distinct",
    "insufficient_evidence",
)


@dataclass(frozen=True)
class ComparisonResult:
    query_unit_id: str
    query_source: str
    query_position: int
    candidate_unit_id: str
    candidate_source: str
    candidate_position: int
    strategy: str = ""
    category: str = "insufficient_evidence"
    shared_terms: tuple = ()
    query_only_terms: tuple = ()
    candidate_only_terms: tuple = ()
    overlap_count: int = 0
    note: str = ""
    candidate_text: str = ""

    @property
    def has_overlap(self) -> bool:
        return bool(self.shared_terms)
