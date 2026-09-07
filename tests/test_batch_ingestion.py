from pathlib import Path

import pytest

from src.living_authenticity.knowledge.chunking.chunker_registry import (
    ChunkerRegistry,
)
from src.living_authenticity.knowledge.cleaning.cleaner import Cleaner
from src.living_authenticity.knowledge.cleaning.normalizer import Normalizer
from src.living_authenticity.knowledge.ingestion.batch import (
    BatchIngestor,
    IngestionOutcome,
)
from src.living_authenticity.knowledge.ingestion.pipeline import (
    IngestionPipeline,
    IngestionResult,
)
from src.living_authenticity.knowledge.metadata.extractor import MetadataExtractor
from src.living_authenticity.knowledge.parser.obsidian_parser import ObsidianParser
from src.living_authenticity.knowledge.readers.reader_registry import ReaderRegistry
from src.living_authenticity.security import PathBoundary


def _pipeline() -> IngestionPipeline:
    return IngestionPipeline(
        reader_registry=ReaderRegistry(),
        chunker_registry=ChunkerRegistry(),
        cleaner=Cleaner(),
        metadata_extractor=MetadataExtractor(),
        parser=ObsidianParser(),
        normalizer=Normalizer(),
    )


def _write(workspace: Path, name: str, content: str) -> Path:
    path = workspace / name
    path.write_text(content, encoding="utf-8")
    return path


def _result(outcome: IngestionOutcome) -> IngestionResult:
    result = outcome.result
    if result is None:
        raise AssertionError("expected a successful outcome")
    return result


SAMPLE_NOTE = (
    "Observation:\nPeople often lose the ability to enjoy calmness.\n"
)


def test_single_file_behavior_is_preserved(tmp_path):
    note = _write(tmp_path, "note.md", SAMPLE_NOTE)

    outcomes = BatchIngestor(
        _pipeline(), PathBoundary(tmp_path)
    ).ingest_many([str(note)])

    outcome = outcomes[0]
    assert len(outcomes) == 1
    assert outcome.is_success is True
    result = _result(outcome)
    parsed = result.parsed
    assert parsed is not None
    assert parsed.note_type == "Observation"


def test_multiple_files_are_processed_in_order(tmp_path):
    one = _write(tmp_path, "one.txt", SAMPLE_NOTE)
    two = _write(tmp_path, "two.md", SAMPLE_NOTE)

    outcomes = BatchIngestor(
        _pipeline(), PathBoundary(tmp_path)
    ).ingest_many([str(one), str(two)])

    assert [outcome.status for outcome in outcomes] == ["success", "success"]
    assert outcomes[0].source == str(one)
    assert outcomes[1].source == str(two)
    assert _result(outcomes[0]).metadata["file_name"] == "one.txt"
    assert _result(outcomes[1]).metadata["file_name"] == "two.md"


def test_supported_formats_are_handled_together(tmp_path):
    md = _write(tmp_path, "a.md", SAMPLE_NOTE)
    txt = _write(tmp_path, "b.txt", SAMPLE_NOTE)

    outcomes = BatchIngestor(
        _pipeline(), PathBoundary(tmp_path)
    ).ingest_many([str(md), str(txt)])

    first, second = outcomes[0], outcomes[1]
    assert [outcome.status for outcome in outcomes] == ["success", "success"]
    assert _result(first).metadata["extension"] == ".md"
    assert _result(second).metadata["extension"] == ".txt"


def test_empty_input_is_rejected_clearly(tmp_path):
    empty = _write(tmp_path, "empty.md", "")

    outcomes = BatchIngestor(
        _pipeline(), PathBoundary(tmp_path)
    ).ingest_many([str(empty)])

    assert outcomes[0].status == "empty"
    assert outcomes[0].is_success is False
    assert outcomes[0].error == "file is empty"


def test_unsupported_extension_is_rejected_clearly(tmp_path):
    binary = tmp_path / "archive.pdf"
    binary.write_bytes(b"pdf content")

    outcomes = BatchIngestor(
        _pipeline(), PathBoundary(tmp_path)
    ).ingest_many([str(binary)])

    outcome = outcomes[0]
    assert outcome.status == "failed"
    assert outcome.error is not None
    assert "No reader registered for" in outcome.error


def test_missing_file_is_rejected_clearly(tmp_path):
    missing = tmp_path / "missing.md"

    outcomes = BatchIngestor(
        _pipeline(), PathBoundary(tmp_path)
    ).ingest_many([str(missing)])

    assert outcomes[0].status == "invalid"
    assert outcomes[0].error == "path is not a readable file"


def test_directory_input_is_rejected_clearly(tmp_path):
    directory = tmp_path / "somedir"
    directory.mkdir()

    outcomes = BatchIngestor(
        _pipeline(), PathBoundary(tmp_path)
    ).ingest_many([str(directory)])

    assert outcomes[0].is_success is False
    assert outcomes[0].status == "invalid"
    assert outcomes[0].error == "path is a directory, not a file"


def test_failure_isolated_and_other_files_still_processed(tmp_path):
    good = _write(tmp_path, "good.md", SAMPLE_NOTE)
    bad = tmp_path / "bad.pdf"
    bad.write_bytes(b"not a text file")

    outcomes = BatchIngestor(
        _pipeline(), PathBoundary(tmp_path)
    ).ingest_many([str(good), str(bad), str(good)])

    assert [outcome.status for outcome in outcomes] == [
        "success",
        "failed",
        "success",
    ]
    assert outcomes[2].is_success is True
    result = _result(outcomes[2])
    parsed = result.parsed
    assert parsed is not None
    assert parsed.note_type == "Observation"


def test_on_failure_hook_receives_each_failed_outcome(tmp_path):
    bad = tmp_path / "bad.xyz"
    bad.write_bytes(b"x")
    good = _write(tmp_path, "good.md", SAMPLE_NOTE)

    reported: list[str] = []
    outcomes = BatchIngestor(
        _pipeline(), PathBoundary(tmp_path)
    ).ingest_many(
        [str(bad), str(good)],
        on_failure=lambda outcome: reported.append(outcome.status),
    )

    assert reported == ["failed"]
    assert outcomes[0].is_success is False
    assert outcomes[1].is_success is True


def test_path_outside_boundary_is_rejected_without_read(tmp_path):
    allowed_root = tmp_path / "allowed"
    allowed_root.mkdir()
    secret = tmp_path / "secret.md"
    secret.write_text(SAMPLE_NOTE, encoding="utf-8")

    outcomes = BatchIngestor(
        _pipeline(), PathBoundary(allowed_root)
    ).ingest_many([str(secret)])

    assert outcomes[0].status == "outside_boundary"
    assert outcomes[0].is_success is False
    assert outcomes[0].error == "path is outside the allowed boundary"
    secret.unlink()