from src.living_authenticity.embedding.service import EmbeddingService
from Config.settings import PATHS


def main():
    model_path = PATHS["models"]["bge_m3"]

    embedding_service = EmbeddingService(model_path)

    vector = embedding_service.embed("سلام دنیا")

    print(f"Embedding dimension: {len(vector)}")
    print(vector[:10])


if __name__ == "__main__":
    main()