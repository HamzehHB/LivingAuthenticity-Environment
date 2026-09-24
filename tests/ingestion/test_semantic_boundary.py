from src.living_authenticity.knowledge.ingestion.chunking.semantic_boundary import (
    SemanticBoundaryDetector,
)


def test_without_embedding_service_similarity_is_zero():
    detector = SemanticBoundaryDetector()

    similarity = detector.similarity(
        "Identity is formed through lived experience.",
        "Selfhood emerges through lived experience.",
    )

    assert similarity == 0.0


def test_without_embedding_service_proposes_split():
    detector = SemanticBoundaryDetector()

    assert detector.should_split("topic one", "topic two") is True
