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
        return bool(self.proposed_type)