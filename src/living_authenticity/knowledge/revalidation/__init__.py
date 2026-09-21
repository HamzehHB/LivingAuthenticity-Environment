"""Validation and revalidation boundary (no execution).

Revalidation checks whether one exact explicitly approved proposal
remains unchanged and eligible for the future controlled-execution
boundary. A passing result never authorizes or performs
execution; it only reports that the approved proposal is unchanged.
"""
from .outcome import REVALIDATION_CHECKS, RevalidationResult
from .revalidator import Revalidator, revalidate_proposal
from .schema_version import current_schema_version

__all__ = ("REVALIDATION_CHECKS", "RevalidationResult", "Revalidator",
    "current_schema_version", "revalidate_proposal")
