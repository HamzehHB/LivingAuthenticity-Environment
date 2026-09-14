"""Abstract Obsidian output generator contract.

Output generation is a read-only representation stage that occurs
after Proposal (and optionally Confidence). It represents existing
analytical results; it must never recompute analysis, decide actions,
authorize changes, mutate inputs, or perform I/O.
"""
from abc import ABC, abstractmethod

from .outcome import GeneratedNote


class ObsidianNoteGenerator(ABC):
    """Render one immutable GeneratedNote for one proposal."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Stable strategy name recorded on generated notes."""
        raise NotImplementedError

    @abstractmethod
    def generate(self, query, proposal=None, classification=None,
                 confidence=None) -> GeneratedNote:
        """Return one immutable note representation for ``proposal``.

        All inputs are read-only evidence produced by earlier stages;
        none of them may be mutated.
        """
        raise NotImplementedError
