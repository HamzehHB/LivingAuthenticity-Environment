from sentence_transformers import SentenceTransformer


class BGEModel:
    def __init__(self, model_path: str):
        self.model = SentenceTransformer(model_path)

    def encode(self, texts):
        return self.model.encode(
            texts,
            normalize_embeddings=True
        )

    def get_dimension(self):
        return len(self.model.encode(["test"])[0])