from Config.settings import PATHS

from src.living_authenticity.embedding.service import EmbeddingService
from src.living_authenticity.database.lancedb_manager import LanceDBManager

from src.living_authenticity.knowledge.readers.txt_reader import TXTReader
from src.living_authenticity.knowledge.cleaning.cleaner import Cleaner
from src.living_authenticity.knowledge.chunking.chunker import Chunker
from src.living_authenticity.knowledge.metadata.extractor import MetadataExtractor
from src.living_authenticity.knowledge.ingestion.pipeline import IngestionPipeline


def main():

    embedding_service = EmbeddingService(PATHS["models"]["bge_m3"])

    database = LanceDBManager()
    database.create_knowledge_vector_table()

    pipeline = IngestionPipeline(
        reader=TXTReader(),
        cleaner=Cleaner(),
        chunker=Chunker(),
        metadata_extractor=MetadataExtractor(),
        embedding_service=embedding_service,
        database=database,
    )

    number_of_chunks = pipeline.ingest(
        r"F:\LivingAuthenticity_Data\Knowledge\Exports\Test\first_note.txt"
    )

    print(f"\nSuccessfully ingested {number_of_chunks} chunk(s).\n")

    print("Current database:\n")
    print(database.show_all())


if __name__ == "__main__":
    main()