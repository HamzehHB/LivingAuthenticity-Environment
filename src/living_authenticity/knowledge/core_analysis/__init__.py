"""Deterministic analytical Core relevance analysis over approved Core evidence.

Core Analysis is a read-only analytical stage. It examines whether a query
knowledge unit appears potentially relevant to supplied approved Core units
using explicit token-overlap rules. It creates, modifies, authorizes, or
persists nothing.

Authoritative Core remains human-controlled. Every result produced here is
explicitly non-authoritative: an analytical observation for human review,
never an approved Core change.
"""

from .analyzer_registry import AnalyzerRegistry
from .base_analyzer import CoreRelevanceAnalyzer
from .outcome import (
    CORE_RELEVANCE_VALUES,
    CoreAnalysisResult,
)
from .token_overlap import DefaultCoreAnalyzer, TokenOverlapCoreAnalyzer

__all__ = (
    "CORE_RELEVANCE_VALUES",
    "AnalyzerRegistry",
    "CoreAnalysisResult",
    "CoreRelevanceAnalyzer",
    "DefaultCoreAnalyzer",
    "TokenOverlapCoreAnalyzer",
)
