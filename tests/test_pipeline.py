from pathlib import Path

from src.living_authenticity.knowledge.readers.reader_registry import ReaderRegistry
from src.living_authenticity.knowledge.chunking.chunker_registry import ChunkerRegistry
from src.living_authenticity.knowledge.cleaning.cleaner import Cleaner
from src.living_authenticity.knowledge.metadata.extractor import MetadataExtractor
from src.living_authenticity.knowledge.ingestion.pipeline import IngestionPipeline
from src.living_authenticity.knowledge.parser.obsidian_parser import ObsidianParser


FIXTURES = Path(__file__).resolve().parent / "test_data"


def _pipeline() -> IngestionPipeline:
    return IngestionPipeline(
        reader_registry=ReaderRegistry(),
        chunker_registry=ChunkerRegistry(),
        cleaner=Cleaner(),
        metadata_extractor=MetadataExtractor(),
        parser=ObsidianParser(),
    )


def test_ingest_txt_fixture_is_analysis_only():
    result = _pipeline().ingest(str(FIXTURES / "example.txt"))

    assert "Observation:" in result.raw_text
    assert result.cleaned_text == result.raw_text
    assert len(result.chunks) >= 1
    assert result.parsed is not None
    assert result.parsed.note_type == "Observation"
    assert "Peace" in result.parsed.relations
    assert "peace" in result.parsed.tags
    assert result.metadata["file_name"] == "example.txt"
    assert "embedding" not in result.metadata
    assert not hasattr(result, "database")


def test_ingest_markdown_fixture():
    result = _pipeline().ingest(str(FIXTURES / "example.md"))

    assert result.metadata["extension"] == ".md"
    assert result.parsed is not None
    assert result.parsed.note_type == "Observation"
    assert "Survival" in result.parsed.relations


def test_ingest_strips_utf8_bom_before_processing(tmp_path):
    note = tmp_path / "bom_note.md"
    note.write_bytes(
        "\ufeff".encode("utf-8")
        + "Observation:\nPeople often lose the ability to enjoy calmness.\n".encode(
            "utf-8"
        )
    )

    result = _pipeline().ingest(str(note))

    assert result.raw_text.startswith("Observation:")
    assert "\ufeff" not in result.raw_text
    assert result.parsed is not None
    assert result.parsed.note_type == "Observation"
    assert "calmness" in result.cleaned_text
