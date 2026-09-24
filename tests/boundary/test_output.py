"""Obsidian output generator tests."""
import copy
import dataclasses

import yaml

from src.living_authenticity.knowledge.analysis.classification.result import (
    ClassificationResult,
)
from src.living_authenticity.knowledge.decision.confidence.outcome import (
    ConfidenceAssessment,
)
from src.living_authenticity.knowledge.ingestion.extraction.knowledge_unit import (
    KnowledgeUnit,
)
from src.living_authenticity.knowledge.output import (
    DefaultOutputGenerator,
    DeterministicObsidianGenerator,
    GeneratedNote,
    ObsidianNoteGenerator,
    OutputGeneratorRegistry,
)
from src.living_authenticity.knowledge.decision.proposal.builder import ProposalBuilder


def _unit(text="A calm morning observation about attention"):
    return KnowledgeUnit(
        id="q1", source="inbox", original_text=text,
        meaning=text, cleaned_text=text, normalized_text=text,
        context="", proposed_type="", position=1,
    )


def _cls():
    return ClassificationResult(
        unit_id="q1", source="inbox", position=1,
        proposed_type="Observation", is_certain=True, rationale="r",
        evidence=("e",), classifier="rule_based_default",
    )


def _proposal(dest="Staging/note.md"):
    return ProposalBuilder().build(_unit(), destination=dest)


def _conf(action="NEEDS_REVIEW"):
    return ConfidenceAssessment(
        query_unit_id="q1", query_source="inbox", query_position=1,
        proposal_action=action, level="weak",
        strategy="evidence_strength", basis="b",
        uncertainties=("gap",),
    )


def test_valid_generation_structure():
    note = DefaultOutputGenerator().generate(
        _unit(), _proposal(), classification=_cls(), confidence=_conf())
    assert note.query_unit_id == "q1"
    assert note.proposal_action in ("CREATE", "DO_NOT_IMPORT", "NEEDS_REVIEW")
    assert note.proposed_type == "Observation"
    assert note.is_authoritative is False
    assert note.requires_human_review is True
    assert note.markdown.startswith("---\n")
    assert "# " in note.markdown
    assert "NON-AUTHORITATIVE" in note.markdown
    assert "Proposed location (inert" in note.markdown


def test_frontmatter_round_trips_safe_yaml():
    note = DefaultOutputGenerator().generate(
        _unit(), _proposal(), classification=_cls(), confidence=_conf())
    front = note.markdown.split("---\n")[1]
    loaded = yaml.safe_load(front)
    assert isinstance(loaded, dict)
    for value in loaded.values():
        assert isinstance(value, (str, int, float, bool, list, dict, type(None)))
    text = yaml.safe_dump(loaded, sort_keys=True)
    assert yaml.safe_load(text) == loaded


def test_meaning_and_provenance_preserved():
    proposal = _proposal()
    note = DefaultOutputGenerator().generate(_unit(), proposal)
    assert "A calm morning observation about attention" in note.markdown
    for item in proposal.provenance:
        assert item in note.markdown
    assert note.uncertainties


def test_inputs_not_mutated():
    query = _unit()
    proposal = _proposal()
    before_q = copy.deepcopy(query)
    before_p = copy.deepcopy(proposal)
    cls = _cls()
    conf = _conf()
    DefaultOutputGenerator().generate(query, proposal, cls, conf)
    assert query == before_q
    assert proposal == before_p


def test_deterministic_output():
    first = DefaultOutputGenerator().generate(
        _unit(), _proposal(), classification=_cls(), confidence=_conf())
    second = DefaultOutputGenerator().generate(
        _unit(), _proposal(), classification=_cls(), confidence=_conf())
    assert first == second
    assert first.markdown == second.markdown


def test_malformed_rejected():
    gen = DefaultOutputGenerator()
    for bad_q, bad_p in (("nope", _proposal()), (_unit(), "nope")):
        try:
            gen.generate(bad_q, bad_p)
            raise AssertionError("expected TypeError")
        except TypeError:
            pass


def test_registry_and_contract():
    assert issubclass(DeterministicObsidianGenerator, ObsidianNoteGenerator)
    reg = OutputGeneratorRegistry()
    assert isinstance(reg.default(), DeterministicObsidianGenerator)
    reg.register("extra", DeterministicObsidianGenerator(strategy="extra"))
    assert reg.get("extra").name == "extra"
    note = DefaultOutputGenerator().generate(_unit(), _proposal())
    try:
        note.title = "x"  # type: ignore
        raise AssertionError("note must be frozen")
    except dataclasses.FrozenInstanceError:
        pass
