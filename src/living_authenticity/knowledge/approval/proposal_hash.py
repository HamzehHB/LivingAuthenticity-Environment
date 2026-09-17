"""Deterministic proposal identity for approval binding."""
import hashlib
import json


def canonical_proposal_hash(payload: dict) -> str:
    """Return sha256 over canonical JSON of the proposal payload."""
    if not isinstance(payload, dict):
        raise TypeError("payload must be a dict")
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def proposal_payload(proposal, confidence=None) -> dict:
    """Extract the exact displayed fields bound by approval."""
    from src.living_authenticity.knowledge.proposal.outcome import Proposal

    if not isinstance(proposal, Proposal):
        raise TypeError("proposal must be a Proposal")
    payload = {
        "query_unit_id": proposal.query_unit_id,
        "query_source": proposal.query_source,
        "query_position": proposal.query_position,
        "action": proposal.action,
        "title": proposal.title,
        "destination": proposal.destination,
        "reason": proposal.reason,
        "evidence": list(proposal.evidence),
        "classification_type": proposal.classification_type,
        "comparison_summary": proposal.comparison_summary,
        "relation_summary": proposal.relation_summary,
        "core_relevance": proposal.core_relevance,
    }
    if confidence is not None:
        from src.living_authenticity.knowledge.confidence.outcome import ConfidenceAssessment

        if not isinstance(confidence, ConfidenceAssessment):
            raise TypeError("confidence must be a ConfidenceAssessment")
        payload["confidence_level"] = confidence.level
    return payload
