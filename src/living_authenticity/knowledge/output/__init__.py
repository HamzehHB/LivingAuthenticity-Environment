"""Obsidian output generation public interface.

The output generator creates a proposed, non-authoritative Obsidian
representation from an already-built analytical Proposal and its
supporting evidence. Generation is representation only: it never
authorizes, approves, executes, writes, or places anything.
"""
from .base_generator import ObsidianNoteGenerator
from .evidence_note import DefaultOutputGenerator, DeterministicObsidianGenerator
from .outcome import GeneratedNote
from .registry import OutputGeneratorRegistry

__all__ = (
    "GeneratedNote",
    "ObsidianNoteGenerator",
    "DeterministicObsidianGenerator",
    "DefaultOutputGenerator",
    "OutputGeneratorRegistry",
)
