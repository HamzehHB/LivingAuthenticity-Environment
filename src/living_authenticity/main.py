from Config.settings import PATHS

from src.living_authenticity.embedding.service import EmbeddingService
from src.living_authenticity.database.lancedb_manager import LanceDBManager


def main():
    EmbeddingService(PATHS["models"]["bge_m3"])

    db_manager = LanceDBManager()
    db_manager.create_knowledge_vector_table()

    print("Embedding Service initialized.")
    print("LanceDB initialized.")
    print("LivingAuthenticity AI initialized successfully.")


if __name__ == "__main__":
    main()