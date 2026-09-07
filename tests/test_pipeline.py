from pathlib import Path

from src.living_authenticity.knowledge.readers.reader_registry import ReaderRegistry
from src.living_authenticity.knowledge.chunking.chunker_registry import ChunkerRegistry
from src.living_authenticity.knowledge.cleaning.cleaner import Cleaner
from src.living_authenticity.knowledge.cleaning.normalizer import Normalizer
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
        normalizer=Normalizer(),
    )


def test_ingest_txt_fixture_is_analysis_only():
    result = _pipeline().ingest(str(FIXTURES / "example.txt"))

    assert "Observation:" in result.raw_text
    assert result.cleaned_text == result.raw_text
    assert result.normalized_text is not None
    assert "Observation:" in result.normalized_text
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


def test_cleaning_normalizes_whitespace_heavy_input(tmp_path):
    note = tmp_path / "messy.md"
    note.write_text(
        "Observation:   \nPeople often    lose    the ability.\n\n\n\nRelations:\n[[Peace]]\n",
        encoding="utf-8",
    )

    result = _pipeline().ingest(str(note))

    # Trailing whitespace removed
    assert "Observation:   \n" not in result.cleaned_text
    # Excessive blank lines collapsed
    assert "\n\n\n" not in result.cleaned_text
    # Multiple spaces collapsed by normalizer
    assert result.normalized_text is not None
    assert "People often    lose" not in result.normalized_text
    assert "People often lose" in result.normalized_text
    # Meaning preserved
    assert result.parsed is not None
    assert result.parsed.note_type == "Observation"
    assert "Peace" in result.parsed.relations


def test_cleaning_normalizes_crlf_line_endings(tmp_path):
    note = tmp_path / "crlf.md"
    note.write_text(
        "Observation:\r\nPeople often lose the ability.\r\n\r\nRelations:\r\n[[Peace]]\r\n",
        encoding="utf-8",
    )

    result = _pipeline().ingest(str(note))

    assert "\r" not in result.cleaned_text
    assert result.parsed is not None
    assert result.parsed.note_type == "Observation"


def test_pipeline_without_normalizer_preserves_backward_compatibility(tmp_path):
    note = tmp_path / "note.md"
    note.write_text(
        "Observation:\nPeople often lose the ability.\n",
        encoding="utf-8",
    )

    pipeline = IngestionPipeline(
        reader_registry=ReaderRegistry(),
        chunker_registry=ChunkerRegistry(),
        cleaner=Cleaner(),
        metadata_extractor=MetadataExtractor(),
        parser=ObsidianParser(),
    )

    result = pipeline.ingest(str(note))

    assert result.normalized_text is None
    assert result.parsed is not None
    assert result.parsed.note_type == "Observation"


def test_pipeline_preserves_original_input_in_raw_text(tmp_path):
    original = "Observation:\nPeople often lose the ability.\n"
    note = tmp_path / "note.md"
    note.write_text(original, encoding="utf-8")

    result = _pipeline().ingest(str(note))

    assert result.raw_text == original


def test_pipeline_cleaned_differs_from_raw_when_dirty(tmp_path):
    note = tmp_path / "dirty.md"
    note.write_text(
        "Observation:   \nPeople often    lose the ability.\n\n\n\n",
        encoding="utf-8",
    )

    result = _pipeline().ingest(str(note))

    assert result.raw_text != result.cleaned_text
    assert result.raw_text.startswith("Observation:   \n")
    assert result.cleaned_text.startswith("Observation:\n")


def test_pipeline_links_and_meaning_preserved_through_transformations(tmp_path):
    note = tmp_path / "note.md"
    note.write_text(
        "Observation:\nPeople often lose the ability to enjoy calmness.\n\nRelations:\n[[Peace]]\n[[Survival]]\n\nTags:\n#peace\n",
        encoding="utf-8",
    )

    result = _pipeline().ingest(str(note))

    assert "[[Peace]]" in result.cleaned_text
    assert "[[Survival]]" in result.cleaned_text
    assert "#peace" in result.cleaned_text
    assert result.normalized_text is not None
    assert "[[Peace]]" in result.normalized_text
    assert "[[Survival]]" in result.normalized_text
    assert "#peace" in result.normalized_text
    assert result.parsed is not None
    assert "Peace" in result.parsed.relations
    assert "Survival" in result.parsed.relations
    assert "peace" in result.parsed.tags
