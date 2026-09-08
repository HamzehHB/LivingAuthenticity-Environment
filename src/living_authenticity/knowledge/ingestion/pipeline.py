from dataclasses import dataclass, field

from src.living_authenticity.knowledge.chunking.chunker_registry import (
    ChunkerRegistry,
)
from src.living_authenticity.knowledge.classification.base_classifier import (
    KnowledgeUnitClassifier,
)
from src.living_authenticity.knowledge.classification.result import (
    ClassificationResult,
)
from src.living_authenticity.knowledge.cleaning.cleaner import Cleaner
from src.living_authenticity.knowledge.cleaning.normalizer import Normalizer
from src.living_authenticity.knowledge.extraction.extractor_registry import (
    ExtractorRegistry,
)
from src.living_authenticity.knowledge.extraction.knowledge_unit import (
    KnowledgeUnit,
)
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
    knowledge_units: list[KnowledgeUnit]
    parsed: ParsedNote | None
    metadata: dict
    classifications: list[ClassificationResult] = field(default_factory=list)


class IngestionPipeline:
    """Pipeline: read, clean, normalize, parse, extract knowledge units, chunk.

    Reader
        ↓
    Cleaner
        ↓
    Normalizer (optional)
        ↓
    Parser (optional)
        ↓
    Knowledge Unit Extraction
        ↓
    Classification (optional)
        ↓
    Chunker
        ↓
    File metadata

    Extraction runs after parsing because ``MarkdownKnowledgeExtractor`` uses
    the parser's ``section_boundaries()`` helper to locate semantic section
    boundaries. The parser instance must therefore be available, and the
    ``parsed`` output is used as a guard so that section-based extraction is
    only applied when the parser successfully parsed the note.

    Classification is an analysis-only, proposal step. When a classifier is
    provided, one :class:`ClassificationResult` is produced per extracted
    :class:`KnowledgeUnit`; the units themselves are never mutated. Without a
    classifier the ``classifications`` list stays empty.

    This pipeline does not embed, store, or write authoritative knowledge.
    """

    def __init__(
        self,
        reader_registry: ReaderRegistry,
        chunker_registry: ChunkerRegistry,
        extractor_registry: ExtractorRegistry,
        cleaner: Cleaner,
        metadata_extractor: MetadataExtractor,
        parser: BaseParser | None = None,
        normalizer: Normalizer | None = None,
        classifier: KnowledgeUnitClassifier | None = None,
    ):

        self.reader_registry = reader_registry
        self.chunker_registry = chunker_registry
        self.extractor_registry = extractor_registry
        self.cleaner = cleaner
        self.metadata_extractor = metadata_extractor
        self.parser = parser
        self.normalizer = normalizer
        self.classifier = classifier

    def ingest(self, file_path: str) -> IngestionResult:

        reader = self.reader_registry.get(file_path)
        raw_text = reader.read(file_path)
        cleaned_text = self.cleaner.clean(raw_text)

        normalized_text = None
        if self.normalizer is not None:
            normalized_text = self.normalizer.normalize(cleaned_text)

        text_for_chunking = normalized_text if normalized_text is not None else cleaned_text

        parsed = None
        if self.parser is not None:
            parsed = self.parser.parse(text_for_chunking)

        knowledge_units: list[KnowledgeUnit] = []
        try:
            extractor = self.extractor_registry.get(file_path)
            knowledge_units = extractor.extract(
                source=file_path,
                original_text=raw_text,
                cleaned_text=cleaned_text,
                normalized_text=normalized_text or cleaned_text,
                parsed=parsed,
                parser=self.parser,
            )
        except ValueError:
            knowledge_units = []

        classifications = []
        if self.classifier is not None:
            classifications = [
                self.classifier.classify(unit) for unit in knowledge_units
            ]

        chunker = self.chunker_registry.get(file_path)
        chunks = chunker.split(text_for_chunking)

        metadata = self.metadata_extractor.extract(file_path)

        return IngestionResult(
            file_path=file_path,
            raw_text=raw_text,
            cleaned_text=cleaned_text,
            normalized_text=normalized_text,
            chunks=chunks,
            knowledge_units=knowledge_units,
            parsed=parsed,
            metadata=metadata,
            classifications=classifications,
        )
