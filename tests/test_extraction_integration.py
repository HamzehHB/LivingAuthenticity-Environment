"""Integration tests for the Knowledge Unit Extraction pipeline.

Verifies that extraction works end-to-end through IngestionPipeline and
BatchIngestor, including the optional-parser fallback path.
"""
from src.living_authenticity.knowledge.cleaning.cleaner import Cleaner
from src.living_authenticity.knowledge.cleaning.normalizer import Normalizer
from src.living_authenticity.knowledge.chunking.chunker_registry import (
    ChunkerRegistry,
)
from src.living_authenticity.knowledge.ingestion.batch import BatchIngestor
from src.living_authenticity.knowledge.ingestion.pipeline import (
    IngestionPipeline,
    IngestionResult,
)
from src.living_authenticity.knowledge.metadata.extractor import MetadataExtractor
from src.living_authenticity.knowledge.extraction.extractor_registry import (
    ExtractorRegistry,
)
from src.living_authenticity.knowledge.parser.obsidian_parser import ObsidianParser
from src.living_authenticity.knowledge.readers.reader_registry import ReaderRegistry
from src.living_authenticity.security import PathBoundary


def _pipeline():
    return IngestionPipeline(
        ReaderRegistry(), ChunkerRegistry(), ExtractorRegistry(),
        Cleaner(), MetadataExtractor(), ObsidianParser(), Normalizer(),
    )


def test_multiple_inputs_through_batch(tmp_path):
    (tmp_path / "a.md").write_text(
        "Observation:\nFirst knowledge unit.\n\n"
        "Concept:\nSecond knowledge unit.\n",
        encoding="utf-8",
    )
    (tmp_path / "b.txt").write_text(
        "Plain paragraph one.\n\nPlain paragraph two.\n",
        encoding="utf-8",
    )

    outcomes = BatchIngestor(_pipeline(), PathBoundary(tmp_path)).ingest_many(
        [str(tmp_path / "a.md"), str(tmp_path / "b.txt")]
    )

    assert len(outcomes) == 2
    assert all(o.is_success for o in outcomes)

    assert outcomes[0].result is not None
    assert outcomes[1].result is not None
    md_result: IngestionResult = outcomes[0].result
    txt_result: IngestionResult = outcomes[1].result

    assert len(md_result.knowledge_units) == 2
    assert len(txt_result.knowledge_units) == 2

    assert all(u.source.endswith("a.md") for u in md_result.knowledge_units)
    assert all(u.source.endswith("b.txt") for u in txt_result.knowledge_units)

    assert md_result.knowledge_units[0].context == "Observation"
    assert md_result.knowledge_units[1].context == "Concept"


def test_pipeline_without_parser_still_extracts(tmp_path):
    pipeline = IngestionPipeline(
        ReaderRegistry(), ChunkerRegistry(), ExtractorRegistry(),
        Cleaner(), MetadataExtractor(), normalizer=Normalizer(),
    )
    (tmp_path / "note.md").write_text(
        "First paragraph.\n\nSecond paragraph.\n",
        encoding="utf-8",
    )
    result = pipeline.ingest(str(tmp_path / "note.md"))
    assert len(result.knowledge_units) == 2
    assert result.parsed is None
