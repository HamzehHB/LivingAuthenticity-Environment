"""Deterministic, explainable classification of knowledge units.

Uses only information already present in a KnowledgeUnit and the canonical
knowledge types from the project schema. No provider, model, or external
dependency is introduced.

Design principles
-----------------
* Structure first: a recognized section label (``unit.context``) is the most
  reliable signal because it is the author's own heading.
* Content second: for unlabeled units, distinctive Persian/English cues are
  scored. A content-only proposal requires at least two distinct cues.
* Uncertainty is explicit: no signal, an ambiguous tie, or too weak evidence
  leaves the result unresolved (``proposed_type=""``, ``is_certain=False``)
  rather than fabricating a type.
* The source KnowledgeUnit is never mutated.
"""

import re

from src.living_authenticity.knowledge.extraction.knowledge_unit import (
    KnowledgeUnit,
)
from src.living_authenticity.knowledge.parser.note_types import NoteType

from .base_classifier import KnowledgeUnitClassifier
from .result import ClassificationResult

# Fixed canonical iteration order keeps scoring deterministic.
_CANONICAL_ORDER = (
    NoteType.CORE,
    NoteType.CONCEPT,
    NoteType.OBSERVATION,
    NoteType.EXPERIENCE,
    NoteType.RESEARCH,
    NoteType.METHOD,
    NoteType.SOURCE,
    NoteType.META,
    NoteType.ARCHIVE,
)

# Minimum number of distinct content cues required before proposing a type
# from content alone (guards against a lone keyword misfiring).
_MIN_CONTENT_CUES = 2

# Section/context labels recognized from the note itself. These mirror the
# labels the parser maps to the same canonical types.
_LABEL_TO_TYPE = {
    "observation": NoteType.OBSERVATION,
    "مشاهده": NoteType.OBSERVATION,
    "مشاهده مطرح شده": NoteType.OBSERVATION,
    "concept": NoteType.CONCEPT,
    "مفاهیم": NoteType.CONCEPT,
    "experience": NoteType.EXPERIENCE,
    "تجربه": NoteType.EXPERIENCE,
    "research": NoteType.RESEARCH,
    "پژوهش": NoteType.RESEARCH,
    "method": NoteType.METHOD,
    "روش": NoteType.METHOD,
    "source": NoteType.SOURCE,
    "منبع": NoteType.SOURCE,
    "core": NoteType.CORE,
    "meta": NoteType.META,
    "archive": NoteType.ARCHIVE,
}

_WS_RE = re.compile(r"\s+")
# Distinct content cues (English + Persian). Cues are written with plain
# spaces; normalization maps ZWNJ to a space so matching is ZWNJ-insensitive.
_CUES_BY_TYPE = {
    NoteType.CORE: (
        "core principle", "governing principle", "foundational principle",
        "اصل بنیادین", "اصل اساسی", "thesis statement",
    ),
    NoteType.CONCEPT: (
        "is defined as", "refers to", "means that", "the concept of",
        "مفهوم", "تعریف می شود", "به این معنا",
    ),
    NoteType.OBSERVATION: (
        "i observed", "i notice that", "people often", "the pattern",
        "it is common that", "متوجه شدم", "اغلب مردم", "الگو",
    ),
    NoteType.EXPERIENCE: (
        "i experienced", "my experience", "i felt", "i went through",
        "تجربه شخصی", "احساس کردم", "از سر گذراندم",
    ),
    NoteType.RESEARCH: (
        "this study", "research shows", "according to", "the hypothesis",
        "the findings", "این پژوهش", "مطالعه نشان می دهد", "بر اساس",
        "فرضیه",
    ),
    NoteType.METHOD: (
        "a method for", "the procedure", "how to", "step by step",
        "this technique", "یک روش برای", "مراحل", "این تکنیک",
    ),
    NoteType.SOURCE: (
        "the source", "this reference", "the book", "according to the paper",
        "منبع", "این مرجع", "کتاب",
    ),
    NoteType.META: (
        "the knowledge base", "this note is", "the knowledge management system",
        "this system stores", "پایگاه دانش", "این سیستم", "مدیریت دانش",
    ),
    NoteType.ARCHIVE: (
        "archived knowledge", "historical record", "previously authoritative",
        "بایگانی شده", "سوابق تاریخی",
    ),
}


def _normalize(text):
    """Case-fold and normalize whitespace and ZWNJ for stable matching."""
    if text is None:
        return ""
    text = text.replace("\u200c", " ").casefold()
    return _WS_RE.sub(" ", text).strip()


class RuleBasedKnowledgeUnitClassifier(KnowledgeUnitClassifier):
    """A deterministic, explainable, dependency-free classifier."""

    def __init__(self):
        self._cue_lists = {
            note_type: tuple(_normalize(cue) for cue in cues)
            for note_type, cues in _CUES_BY_TYPE.items()
        }
        self._label_lookup = {
            _normalize(label): note_type
            for label, note_type in _LABEL_TO_TYPE.items()
        }
        self._name = "rule_based_default"

    @property
    def name(self):
        return self._name

    def classify(self, unit):
        label_type = self._label_type(unit.context)
        if label_type is not None:
            return self._proposal(
                unit, label_type.value, True,
                "The section/context label identifies the canonical type "
                f"'{label_type.value}'.",
                (f"context_label:{_normalize(unit.context)}",),
            )

        text = _normalize(unit.cleaned_text or unit.original_text or unit.meaning or "")
        if not text:
            return self._proposal(
                unit, "", False,
                "No analyzable content is present.", ("empty_content",),
            )

        matched = self._matched(text)
        best_type, best_score, second = self._rank(matched)

        if best_score < _MIN_CONTENT_CUES or best_score == second:
            return self._proposal(
                unit, "", False,
                "Content evidence is insufficient or ambiguous to choose a "
                "canonical type; no type was proposed.",
                tuple(f"matched:{cue}" for cue, _ in matched),
            )

        # At this point best_score >= 2 with a strict winner, so a best type
        # always exists. The assert documents that invariant for checkers.
        assert best_type is not None

        cues_for_best = tuple(
            cue for cue, note_type in matched if note_type is best_type
        )
        return self._proposal(
            unit, best_type.value, True,
            f"Content cues indicate the canonical type '{best_type.value}'.",
            tuple(f"cue:{cue}" for cue in cues_for_best),
        )

    def _label_type(self, context):
        if not context:
            return None
        return self._label_lookup.get(_normalize(context))

    def _matched(self, text):
        matched = []
        for note_type in _CANONICAL_ORDER:
            for cue in self._cue_lists[note_type]:
                if cue and cue in text:
                    matched.append((cue, note_type))
        return matched

    @staticmethod
    def _rank(matched) -> "tuple":
        scores = {}
        for _, note_type in matched:
            scores[note_type] = scores.get(note_type, 0) + 1
        best_type = None
        best_score = 0
        second_score = 0
        for note_type in _CANONICAL_ORDER:
            score = scores.get(note_type, 0)
            if score > best_score:
                second_score = best_score
                best_score = score
                best_type = note_type
            elif score > second_score:
                second_score = score
        return best_type, best_score, second_score

    @staticmethod
    def _proposal(unit, proposed_type, is_certain, rationale, evidence):
        return ClassificationResult(
            unit_id=unit.id,
            source=unit.source,
            position=unit.position,
            proposed_type=proposed_type,
            is_certain=is_certain,
            rationale=rationale,
            evidence=evidence,
            classifier="rule_based_default",
        )


# Short, stable alias used as the default classifier.
DefaultClassifier = RuleBasedKnowledgeUnitClassifier