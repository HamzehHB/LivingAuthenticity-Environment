"""Deterministic analytical comparison of knowledge units.

Comparison consumes retrieved candidates as evidence and produces
read-only analytical results. It decides nothing and authorizes nothing.
"""

from .base_comparator import KnowledgeComparator
from .comparator_registry import ComparatorRegistry
from .outcome import COMPARISON_CATEGORIES, ComparisonResult
from .token_overlap import (
    DefaultComparator,
    TokenOverlapComparator,
    comparison_tokens,
    normalize_text,
)

__all__ = (
    "COMPARISON_CATEGORIES",
    "ComparisonResult",
    "ComparatorRegistry",
    "DefaultComparator",
    "KnowledgeComparator",
    "TokenOverlapComparator",
    "comparison_tokens",
    "normalize_text",
)
