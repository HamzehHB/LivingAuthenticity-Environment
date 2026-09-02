from src.living_authenticity.knowledge.cleaning.cleaner import (
    Cleaner,
)

from src.living_authenticity.knowledge.metadata.extractor import (
    MetadataExtractor,
)

from src.living_authenticity.knowledge.ingestion.pipeline import (
    IngestionPipeline,
)

from src.living_authenticity.knowledge.readers.reader_registry import (
    ReaderRegistry,
)

from src.living_authenticity.knowledge.chunking.chunker_registry import (
    ChunkerRegistry,
)

from src.living_authenticity.knowledge.parser.obsidian_parser import (
    ObsidianParser,
)


def main():

    reader_registry = ReaderRegistry()

    chunker_registry = ChunkerRegistry()

    cleaner = Cleaner()

    metadata = MetadataExtractor()

    parser = ObsidianParser()

    pipeline = IngestionPipeline(
        reader_registry=reader_registry,
        chunker_registry=chunker_registry,
        cleaner=cleaner,
        metadata_extractor=metadata,
        parser=parser,
    )

    print("Reader Registry initialized.")

    print("Chunker Registry initialized.")

    print("Parser initialized.")

    print("Pipeline initialized.")

    print("LivingAuthenticity Environment initialized successfully.")

    return pipeline


if __name__ == "__main__":
    main()
