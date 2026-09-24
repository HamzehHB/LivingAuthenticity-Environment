"""Controlled-execution tests (synthetic tmp_path staging only)."""
from src.living_authenticity.knowledge.governance.approval.explicit_gate import (
    ExplicitApprovalGate,
)
from src.living_authenticity.knowledge.decision.confidence.outcome import (
    ConfidenceAssessment,
)
from src.living_authenticity.knowledge.governance.execution import (
    ControlledExecutor,
    execute_create,
)
from src.living_authenticity.knowledge.ingestion.extraction.knowledge_unit import (
    KnowledgeUnit,
)
from src.living_authenticity.knowledge.output.evidence_note import (
    DefaultOutputGenerator,
)
from src.living_authenticity.knowledge.decision.proposal.outcome import Proposal


def _query():
    return KnowledgeUnit(
        id="u1", source="src", original_text="hello",
        meaning="hello", position=0,
    )


def _proposal(**over):
    base = {
        "query_unit_id": "u1", "query_source": "src",
        "query_position": 0, "action": "CREATE",
        "title": "Title One", "destination": "Inbox suggestion",
        "reason": "evidence supports a new draft",
        "provenance": ("query:u1@src#0",),
    }
    base.update(over)
    return Proposal(**base)


def _confidence():
    return ConfidenceAssessment(
        query_unit_id="u1", query_source="src", query_position=0,
        proposal_action="CREATE", level="weak",
    )


_DEFAULT = object()


def _chain(proposal=None, confidence=_DEFAULT, answer="y"):
    gate = ExplicitApprovalGate()
    query = _query()
    prop = proposal if proposal is not None else _proposal()
    if confidence is _DEFAULT:
        conf = _confidence()
    else:
        conf = confidence
    request = gate.build_request(query, prop, conf)
    outcome = gate.decide(request, answer)
    note = DefaultOutputGenerator().generate(query, proposal=prop, confidence=conf)
    return (request, outcome, prop, conf, note)


def test_valid_create_writes_hash_artifact(tmp_path):
    request, outcome, prop, conf, note = _chain()
    result = execute_create(request, outcome, prop, conf, note, tmp_path)
    assert result.attempted and result.permitted and result.executed
    assert result.proposal_hash == request.proposal_hash
    assert result.action == "CREATE"
    assert result.artifact_path == request.proposal_hash + ".md"
    assert result.revalidation_valid is True
    assert result.is_authoritative is False
    assert result.requires_human_review is True
    target = tmp_path / result.artifact_path
    assert target.is_file()
    assert target.read_text(encoding="utf-8") == note.markdown


def test_destination_is_inert_not_a_path(tmp_path):
    request, outcome, prop, conf, note = _chain(
        proposal=_proposal(destination="../../evil-absolute"))
    result = execute_create(request, outcome, prop, conf, note, tmp_path)
    assert result.executed is True
    assert (tmp_path / (request.proposal_hash + ".md")).is_file()


def test_rejected_approval_cannot_execute(tmp_path):
    request, outcome, prop, conf, note = _chain(answer="n")
    result = execute_create(request, outcome, prop, conf, note, tmp_path)
    assert result.executed is False and result.permitted is False
    assert result.failed_check == "approval_binding"
    assert list(tmp_path.iterdir()) == []


def test_foreign_hash_cannot_execute(tmp_path):
    import dataclasses
    request, outcome, prop, conf, note = _chain()
    other = _chain(proposal=_proposal(title="Other Title"))[0]
    forged = dataclasses.replace(outcome, proposal_hash=other.proposal_hash)
    result = execute_create(request, forged, prop, conf, note, tmp_path)
    assert result.executed is False
    assert list(tmp_path.iterdir()) == []


def test_changed_contents_cannot_execute(tmp_path):
    request, outcome, prop, conf, note = _chain()
    changed = _proposal(title="Changed After Approval")
    result = execute_create(request, outcome, changed, conf, note, tmp_path)
    assert result.executed is False
    assert list(tmp_path.iterdir()) == []


def test_changed_destination_cannot_execute(tmp_path):
    request, outcome, prop, conf, note = _chain()
    changed = _proposal(destination="Somewhere else")
    result = execute_create(request, outcome, changed, conf, note, tmp_path)
    assert result.executed is False
    assert list(tmp_path.iterdir()) == []


def test_non_create_actions_rejected(tmp_path):
    for action in ("DO_NOT_IMPORT", "NEEDS_REVIEW"):
        request, outcome, prop, conf, note = _chain(
            proposal=_proposal(action=action))
        gate_note = note
        import dataclasses
        gate_note = dataclasses.replace(note, proposal_action=action)
        result = execute_create(
            request, outcome, prop, conf, gate_note, tmp_path)
        assert result.executed is False
        assert result.failed_check == "action_eligibility"
    assert list(tmp_path.iterdir()) == []


def test_unsupported_action_coerced_and_rejected(tmp_path):
    request, outcome, prop, conf, note = _chain(
        proposal=_proposal(action="UPDATE"))
    assert prop.action == "NEEDS_REVIEW"
    result = execute_create(request, outcome, prop, conf, note, tmp_path)
    assert result.executed is False


def test_no_overwrite_existing_artifact(tmp_path):
    request, outcome, prop, conf, note = _chain()
    first = execute_create(request, outcome, prop, conf, note, tmp_path)
    assert first.executed is True
    target = tmp_path / first.artifact_path
    target.write_text("human content", encoding="utf-8")
    second = execute_create(request, outcome, prop, conf, note, tmp_path)
    assert second.executed is False
    assert second.failed_check == "destination"
    assert target.read_text(encoding="utf-8") == "human content"


def test_missing_staging_root_rejected(tmp_path):
    request, outcome, prop, conf, note = _chain()
    result = execute_create(request, outcome, prop, conf, note, None)
    assert result.executed is False
    assert result.failed_check == "destination"
    assert list(tmp_path.iterdir()) == []


def test_write_failure_reports_explicit_failure(tmp_path, monkeypatch):
    import pathlib
    request, outcome, prop, conf, note = _chain()
    expected = tmp_path / (request.proposal_hash + ".md")
    assert not expected.exists()

    def _boom(self, *args, **kwargs):
        raise OSError("simulated staging write failure")

    monkeypatch.setattr(pathlib.Path, "write_text", _boom)
    result = execute_create(request, outcome, prop, conf, note, tmp_path)
    assert result.attempted is True
    assert result.permitted is False
    assert result.executed is False
    assert result.failed_check == "destination"
    assert result.reason == "staging write failed"
    assert result.revalidation_valid is False
    assert not expected.exists()
    assert list(tmp_path.iterdir()) == []


def test_missing_note_content_rejected(tmp_path):
    import dataclasses
    request, outcome, prop, conf, note = _chain()
    empty = dataclasses.replace(note, markdown="")
    result = execute_create(request, outcome, prop, conf, empty, tmp_path)
    assert result.executed is False
    assert list(tmp_path.iterdir()) == []


def test_mismatched_note_rejected(tmp_path):
    other_query = KnowledgeUnit(
        id="u2", source="src", original_text="other",
        meaning="other", position=1,
    )
    request, outcome, prop, conf, _note = _chain()
    other_prop = _proposal(query_unit_id="u2", query_position=1,
                           provenance=("query:u2@src#1",))
    other_note = DefaultOutputGenerator().generate(other_query, proposal=other_prop)
    result = execute_create(request, outcome, prop, conf, other_note, tmp_path)
    assert result.executed is False
    assert list(tmp_path.iterdir()) == []


def test_determinism_same_input_same_outcome(tmp_path):
    first_chain = _chain()
    result_cls = ControlledExecutor().execute(*first_chain, staging_root=tmp_path)
    assert result_cls.executed is True
    (tmp_path / result_cls.artifact_path).unlink()
    second_chain = _chain()
    again = ControlledExecutor().execute(*second_chain, staging_root=tmp_path)
    assert again.executed is True
    assert again.artifact_path == result_cls.artifact_path
    assert again.proposal_hash == result_cls.proposal_hash


def test_single_execution_writes_single_file(tmp_path):
    request, outcome, prop, conf, note = _chain()
    result = execute_create(request, outcome, prop, conf, note, tmp_path)
    assert result.executed is True
    assert [p.name for p in tmp_path.iterdir()] == [result.artifact_path]

