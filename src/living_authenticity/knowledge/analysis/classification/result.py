
# Canonical knowledge-type vocabulary for classification proposals.
# Only these values (or "" for unresolved) may survive as a proposed type.
# Unknown values must coerce conservatively to unresolved.
CLASSIFICATION_TYPES = (
    "Core",
    "Concept",
    "Observation",
    "Experience",
    "Research",
    "Method",
    "Source",
    "Meta",
    "Archive",
)

from dataclasses import dataclass


@dataclass(frozen=True)
class ClassificationResult:
    """An analytical classification proposal for one knowledge unit.

    Classification is a proposal, never an authoritative decision. This result
    is produced separately from the source :class:`KnowledgeUnit`, which is
    never mutated by classification.

    ``proposed_type`` holds a canonical knowledge type when the classifier is
    sufficiently confident, or an empty string when the evidence is
    insufficient or ambiguous. In that case ``is_certain`` is ``False`` so the
    uncertainty is explicit rather than fabricated certainty.
    """

    unit_id: str
    source: str
    position: int
    proposed_type: str = ""
    is_certain: bool = False
    rationale: str = ""
    evidence: tuple[str, ...] = ()
    classifier: str = ""

    @property
    def is_resolved(self) -> bool:
        """True when a canonical type was proposed."""
        return self.proposed_type in CLASSIFICATION_TYPES

    def __post_init__(self) -> None:
        """Enforce conservative invariants on direct construction.

        Builders only emit canonical types (or "" when unresolved), but
        direct construction must also be conservative: an unknown
        proposed_type coerces to unresolved ("" with is_certain False),
        and an empty proposed_type can never carry is_certain True.
        Frozen dataclass, so bypass via object.
        """
        if self.proposed_type not in CLASSIFICATION_TYPES and self.proposed_type != "":
            object.__setattr__(self, "proposed_type", "")
            object.__setattr__(self, "is_certain", False)
        elif not self.proposed_type:
            object.__setattr__(self, "is_certain", False)
            