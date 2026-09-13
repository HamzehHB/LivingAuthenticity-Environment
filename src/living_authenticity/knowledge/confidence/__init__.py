"""Confidence stage public interface.

Confidence is an analytical signal describing the strength of the
existing proposal/evidence state. It occurs after Proposal and before
the Knowledge Filter. It is not authorization, approval, or execution,
and it never replaces Human Review.
"""

from .base_guard import ConfidenceGuard
from .evidence_strength import DefaultConfidenceGuard
from .guard_registry import ConfidenceGuardRegistry
from .outcome import CONFIDENCE_LEVELS, ConfidenceAssessment

__all__ = (
    "CONFIDENCE_LEVELS",
    "ConfidenceAssessment",
    "ConfidenceGuard",
    "DefaultConfidenceGuard",
    "ConfidenceGuardRegistry",
)
