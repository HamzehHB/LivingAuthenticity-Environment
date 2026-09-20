"""Validation and revalidation boundary (no execution).

Revalidation checks whether one exact explicitly approved proposal
remains unchanged and eligible for the future controlled-execution
boundary. A passing result never authorizes or performs
execution; it only reports that the approved proposal is unchanged.
"""
from .outcome import REVALIDATION_CHECKS, RevalidationResult
from .revalidator import Revalidator, revalidate_proposal

__all__ = ("REVALIDATION_CHECKS", "RevalidationResult", "Revalidator", "revalidate_proposal")
