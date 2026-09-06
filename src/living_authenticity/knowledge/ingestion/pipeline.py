from dataclasses import dataclass

from src.living_authenticity.knowledge.chunking.chunker_registry import (
    ChunkerRegistry,
)
from src.living_authenticity.knowledge.cleaning.cleaner import Cleaner
from src.living_authenticity.knowledge.metadata.extractor import MetadataExtractor
from src.living_authenticity.knowledge.parser.base_parser import BaseParser
from src.living_authenticity.knowledge.parser.parsed_note import ParsedNote
from src.living_authenticity.knowledge.readers.reader_registry import ReaderRegistry


@dataclass
class IngestionResult:
    """Analysis-only output of one file. No authoritative write."""

    file_path: str
    raw_text: str
    cleaned_text: str
    chunks: list[str]
    parsed: ParsedNote | None
    metadata: dict


class IngestionPipeline:
    """
    Current stage: read, clean, chunk, and parse.

    Reader
        ↓
    Cleaner
        ↓
    Chunker
        ↓
    Parser (optional)
        ↓
    File metadata

    This pipeline does not embed, store, or write authoritative knowledge.
    """

    def __init__(
        self,
        reader_registry: ReaderRegistry,
        chunker_registry: ChunkerRegistry,
        cleaner: Cleaner,
        metadata_extractor: MetadataExtractor,
        parser: BaseParser | None = None,
    ):

        self.reader_registry = reader_registry
        self.chunker_registry = chunker_registry
        self.cleaner = cleaner
        self.metadata_extractor = metadata_extractor
        self.parser = parser

    def ingest(self, file_path: str) -> IngestionResult:

        reader = self.reader_registry.get(file_path)
        raw_text = reader.read(file_path)
        cleaned_text = self.cleaner.clean(raw_text)
        chunker = self.chunker_registry.get(file_path)
        chunks = chunker.split(cleaned_text)

        parsed = None
        if self.parser is not None:
            parsed = self.parser.parse(cleaned_text)

        metadata = self.metadata_extractor.extract(file_path)

        return IngestionResult(
            file_path=file_path,
            raw_text=raw_text,
            cleaned_text=cleaned_text,
            chunks=chunks,
            parsed=parsed,
            metadata=metadata,
        )
