"""Decision-support family (analytical only).

Turns already-gathered evidence into a reviewable, non-authoritative
recommendation:

* ``proposal``        -- the proposed action + representation intent
* ``confidence``      -- ordinal evidence-strength assessment
* ``knowledge_filter``-- analytical boundary/filter signal

Nothing here approves, authorizes, validates, executes, or writes.
Approval, revalidation, execution, and audit live in
``knowledge.governance``.

Deliberately contains no eager imports of the subpackages, so that
importing one decision member cannot trigger another family's chain.
"""
from .filter_outcome import FILTER_VERDICTS, FilterOutcome
from .knowledge_filter import KnowledgeFilter

__all__ = ("FILTER_VERDICTS", "FilterOutcome", "KnowledgeFilter")
