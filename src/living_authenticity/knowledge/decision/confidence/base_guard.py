"""Abstract confidence guard contract.

Confidence is a read-only analytical stage that occurs after Proposal.
It describes the strength of existing evidence; it must never decide
actions, authorize changes, mutate units or proposals, or perform I/O.
"""

from abc import ABC, abstractmethod

from .outcome import ConfidenceAssessment


class ConfidenceGuard(ABC):
    """Produce a descriptive confidence assessment for one proposal."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Stable strategy name recorded on confidence assessments."""
        raise NotImplementedError

    @abstractmethod
    def assess(self, query, proposal=None, classification=None,
               retrieval=None, comparisons=(), relation=None,
               core=None) -> ConfidenceAssessment:
        """Return one immutable confidence assessment for ``proposal``.

        All inputs are read-only evidence produced by earlier stages;
        none of them may be mutated.
        """
        raise NotImplementedError
