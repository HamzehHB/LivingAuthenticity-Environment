from Config.settings import PATHS

from src.living_authenticity.embedding.service import EmbeddingService
from src.living_authenticity.database.lancedb_manager import LanceDBManager


def main():
    model_path = PATHS["models"]["bge_m3"]

    embedding_service = EmbeddingService(model_path)

    vector = embedding_service.embed("سلام دنیا")

    print(f"Embedding dimension: {len(vector)}")
    print(vector[:10])

    db_manager = LanceDBManager()

    print("LanceDB connected successfully.")


if __name__ == "__main__":
    main()