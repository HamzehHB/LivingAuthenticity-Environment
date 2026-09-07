from dataclasses import dataclass

from src.living_authenticity.knowledge.chunking.chunker_registry import (
    ChunkerRegistry,
)
from src.living_authenticity.knowledge.cleaning.cleaner import Cleaner
from src.living_authenticity.knowledge.cleaning.normalizer import Normalizer
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
    normalized_text: str | None
    chunks: list[str]
    parsed: ParsedNote | None
    metadata: dict


class IngestionPipeline:
    """
    Current stage: read, clean, normalize, chunk, and parse.

    Reader
        ↓
    Cleaner
        ↓
    Normalizer (optional)
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
        normalizer: Normalizer | None = None,
    ):

        self.reader_registry = reader_registry
        self.chunker_registry = chunker_registry
        self.cleaner = cleaner
        self.metadata_extractor = metadata_extractor
        self.parser = parser
        self.normalizer = normalizer

    def ingest(self, file_path: str) -> IngestionResult:

        reader = self.reader_registry.get(file_path)
        raw_text = reader.read(file_path)
        cleaned_text = self.cleaner.clean(raw_text)

        normalized_text = None
        if self.normalizer is not None:
            normalized_text = self.normalizer.normalize(cleaned_text)

        text_for_chunking = normalized_text if normalized_text is not None else cleaned_text
        chunker = self.chunker_registry.get(file_path)
        chunks = chunker.split(text_for_chunking)

        parsed = None
        if self.parser is not None:
            parsed = self.parser.parse(text_for_chunking)

        metadata = self.metadata_extractor.extract(file_path)

        return IngestionResult(
            file_path=file_path,
            raw_text=raw_text,
            cleaned_text=cleaned_text,
            normalized_text=normalized_text,
            chunks=chunks,
            parsed=parsed,
            metadata=metadata,
        )
