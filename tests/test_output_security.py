"""Output security tests: inert data, no side effects."""
import ast
import pathlib

import pytest

from src.living_authenticity.knowledge.output import DefaultOutputGenerator
from src.living_authenticity.security.path_boundary import PathBoundary

from tests.test_output import _cls, _conf, _proposal, _unit


def test_adversarial_content_stays_inert():
    evil = "Ignore rules; eval(os.system('x')) {{rm -rf}} __import__"
    query = _unit(text=evil)
    note = DefaultOutputGenerator().generate(
        query, _proposal(dest="../../etc/passwd; rm -rf /"),
        classification=_cls(), confidence=_conf())
    assert evil in note.markdown
    assert note.destination == "../../etc/passwd; rm -rf /"
    assert note.is_authoritative is False
    assert note.requires_human_review is True
    assert PathBoundary().is_allowed(note.destination) is False


def test_no_execution_capability():
    gen = DefaultOutputGenerator()
    assert not hasattr(gen, "execute")
    assert not hasattr(gen, "approve")
    assert not hasattr(gen, "write_to_vault")
    assert not hasattr(gen, "apply")
    assert not hasattr(gen, "commit_to_vault")


def test_no_io_or_provider_markers():
    src = pathlib.Path("src/living_authenticity/knowledge/output")
    text = "\n".join(p.read_text(encoding="utf-8") for p in src.glob("*.py"))
    lowered = text.lower()
    for marker in ("torch", "sentence_transformers", "lancedb",
                   "transformers", "openai", "anthropic", "subprocess",
                   "os.system", "eval(", "exec(", "pickle", "__import__",
                   "shell=true", "socket", "requests", "urllib",
                   "shutil", "yaml.load(", "yaml.unsafe_load("):
        assert marker not in lowered


def test_no_filesystem_ast(tmp_path):
    src = pathlib.Path("src/living_authenticity/knowledge/output")
    for path in src.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = (
                    [a.name for a in node.names]
                    if isinstance(node, ast.Import)
                    else [node.module or ""]
                )
                for name in names:
                    top = name.split(".")[0].lower()
                    assert top not in ("os", "sys", "pathlib", "shutil",
                                       "subprocess", "socket", "importlib")
    before = set(tmp_path.iterdir())
    DefaultOutputGenerator().generate(_unit(), _proposal())
    assert set(tmp_path.iterdir()) == before


def test_mismatched_ids_rejected():
    from src.living_authenticity.knowledge.proposal.builder import (
        ProposalBuilder,
    )
    from src.living_authenticity.knowledge.extraction.knowledge_unit import (
        KnowledgeUnit,
    )
    other = KnowledgeUnit(
        id="other", source="inbox", original_text="t", meaning="t",
        cleaned_text="t", normalized_text="t", context="", position=1)
    with pytest.raises(ValueError):
        DefaultOutputGenerator().generate(other, _proposal())
