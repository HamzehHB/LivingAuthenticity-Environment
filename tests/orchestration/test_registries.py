import pytest

from src.living_authenticity.knowledge.ingestion.chunking.chunker_registry import (
    ChunkerRegistry,
)
from src.living_authenticity.knowledge.ingestion.chunking.paragraph_chunker import (
    ParagraphChunker,
)
from src.living_authenticity.knowledge.ingestion.readers.reader_registry import (
    ReaderRegistry,
)
from src.living_authenticity.knowledge.ingestion.readers.txt_reader import TXTReader


def test_reader_registry_returns_reader_for_known_extension():
    assert ReaderRegistry().get("note.md") is not None


def test_reader_registry_fails_fast_for_unknown_extension():
    with pytest.raises(ValueError, match="No reader registered"):
        ReaderRegistry().get("archive.pdf")


def test_reader_registry_accepts_custom_registration():
    registry = ReaderRegistry()
    custom = TXTReader()

    registry.register(".custom", custom)

    assert registry.get("file.CUSTOM") is custom


def test_chunker_registry_returns_chunker_for_known_extension():
    assert ChunkerRegistry().get("note.md") is not None


def test_chunker_registry_fails_fast_for_unknown_extension():
    with pytest.raises(ValueError, match="No chunker registered"):
        ChunkerRegistry().get("archive.pdf")


def test_chunker_registry_accepts_custom_registration():
    registry = ChunkerRegistry()
    custom = ParagraphChunker()

    registry.register(".custom", custom)

    assert registry.get("file.CUSTOM") is custom
