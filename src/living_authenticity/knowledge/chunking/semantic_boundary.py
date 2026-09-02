class SemanticBoundaryDetector:
    """
    Detects semantic topic boundaries using embeddings when provided.

    Without an embedding service this detector does not call models or
    external systems. Similarity is treated as 0.0, so a split is proposed.
    """

    def __init__(self, embedding_service=None, threshold: float = 0.65):
        self.embedding_service = embedding_service
        self.threshold = threshold

    def similarity(self, previous_text: str, current_text: str) -> float:

        if self.embedding_service is None:
            return 0.0

        import numpy as np

        emb1 = self.embedding_service.embed(previous_text)
        emb2 = self.embedding_service.embed(current_text)

        return float(np.dot(emb1, emb2))

    def should_split(self, previous_text: str, current_text: str) -> bool:

        similarity = self.similarity(previous_text, current_text)

        return similarity < self.threshold
