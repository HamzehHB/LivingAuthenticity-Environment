"""Composition/orchestration package.

Composition only: ``EvidenceFirstPipeline`` wires the existing stage
components together in the contractual evidence-first order and exposes
inspectable intermediate results. It contains no stage logic, no new
decision logic, and no authorization. ``STAGE_ORDER`` remains the single
authoritative runtime order.
"""

from .orchestrator import (
    STAGE_ORDER,
    EvidenceFirstPipeline,
    IntegratedResult,
    IntegratedUnitResult,
)

__all__ = (
    "STAGE_ORDER",
    "EvidenceFirstPipeline",
    "IntegratedResult",
    "IntegratedUnitResult",
)
