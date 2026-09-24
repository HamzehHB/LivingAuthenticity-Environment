"""Analysis / evidence family.

Gathers and interprets evidence over already-prepared knowledge units:
retrieval, comparison, relation analysis, Core analysis, and the
downstream classification proposal. All members are deterministic,
provider-independent, read-only, and non-authoritative.

Directory layout does NOT define runtime order. The authoritative
evidence-first order (retrieval before classification; classification
never an early gate or retrieval prerequisite) is defined by
``STAGE_ORDER`` in ``knowledge.orchestration.orchestrator``.

Deliberately contains no eager imports of the family's own modules, so
that importing one analysis member cannot trigger another family's
import chain.
"""
