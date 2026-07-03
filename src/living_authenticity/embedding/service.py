from .loader import load_embedding_model


class EmbeddingService:
    def __init__(self, model_path: str):
        self.model = load_embedding_model(model_path)

    def embed(self, text: str):
        return self.model.encode([text])[0]