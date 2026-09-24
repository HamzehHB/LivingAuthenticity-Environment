"""Deterministic token-overlap comparison logic."""

import re
import unicodedata
from collections.abc import Sequence
from typing import Any

from src.living_authenticity.knowledge.ingestion.extraction.knowledge_unit import KnowledgeUnit
from src.living_authenticity.knowledge.analysis.retrieval.candidate import RetrievedCandidate

from .base_comparator import KnowledgeComparator
from .outcome import ComparisonResult

_WS_RE = re.compile(r"\s+")
_NON_TOKEN_RE = re.compile(r"[^\w\s]", re.UNICODE)


def normalize_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    normalized = unicodedata.normalize("NFC", text).lower()
    cleaned = normalized.replace(chr(0x200C), " ")
    return cleaned


def comparison_tokens(text: str) -> tuple:
    cleaned = _NON_TOKEN_RE.sub(" ", normalize_text(text))
    tokens = {
        t for t in _WS_RE.split(cleaned)
        if t and any(c.isalpha() for c in t)
    }
    return tuple(sorted(tokens))


def unit_text(unit: KnowledgeUnit) -> str:
    return (
        unit.cleaned_text or unit.normalized_text
        or unit.meaning or unit.original_text or ""
    )


def lookup_text(unit_id: str, lookup: dict) -> str:
    unit = lookup.get(unit_id) if lookup else None
    if isinstance(unit, KnowledgeUnit):
        return unit_text(unit)
    return ""


def categorize(query_text: str, candidate_text: str, shared: tuple) -> tuple:
    if not query_text.strip() or not candidate_text.strip():
        return ("insufficient_evidence", "No analyzable content on one side.")
    if normalize_text(query_text) == normalize_text(candidate_text):
        return ("identical_content", "Normalized texts are identical.")
    qset = set(comparison_tokens(query_text))
    cset = set(comparison_tokens(candidate_text))
    if not qset or not cset:
        return ("insufficient_evidence", "No content tokens on one side.")
    inter = set(shared)
    smaller = min(len(qset), len(cset))
    contain = len(inter) / smaller if smaller else 0.0
    union = len(qset | cset)
    jaccard = len(inter) / union if union else 0.0
    if contain >= 0.9 and jaccard >= 0.8:
        return ("possible_duplicate", "Strong overlap; review still required.")
    if len(inter) >= 2 and contain >= 0.5:
        return ("related_but_distinct", "Overlap with distinct residual content.")
    if not inter:
        return ("distinct", "No shared content tokens observed.")
    return ("distinct", "Overlap too weak to treat units as related.")


class TokenOverlapComparator(KnowledgeComparator):
    def __init__(self) -> None:
        self._name = "token_overlap_comparison"

    @property
    def name(self) -> str:
        return self._name

    def compare(
        self, query: KnowledgeUnit, candidates: Sequence[Any],
        lookup: dict | None = None,
    ) -> tuple:
        if not isinstance(query, KnowledgeUnit):
            raise TypeError("query must be a KnowledgeUnit")
        if candidates is None:
            raise TypeError("candidates must be a sequence")
        qtext = unit_text(query)
        results = []
        for cand in candidates:
            if not isinstance(cand, RetrievedCandidate):
                raise TypeError("candidates must hold RetrievedCandidate objects")
            ctext = lookup_text(cand.unit_id, dict(lookup) if lookup else {})
            if not ctext:
                ctext = cand.text
            qtokens = set(comparison_tokens(qtext))
            ctokens = set(comparison_tokens(ctext))
            shared = tuple(sorted(qtokens & ctokens))
            qonly = tuple(sorted(qtokens - ctokens))
            conly = tuple(sorted(ctokens - qtokens))
            category, note = categorize(qtext, ctext, shared)
            results.append(ComparisonResult(
                query_unit_id=query.id, query_source=query.source,
                query_position=query.position,
                candidate_unit_id=cand.unit_id, candidate_source=cand.source,
                candidate_position=cand.position, strategy=self._name,
                category=category, shared_terms=shared,
                query_only_terms=qonly, candidate_only_terms=conly,
                overlap_count=len(shared), note=note, candidate_text=ctext,
            ))
        return tuple(results)


class DefaultComparator(TokenOverlapComparator):
    """Default comparator alias preserving token-overlap behavior."""
