from src.living_authenticity.knowledge.pipeline import EvidenceFirstPipeline


def main() -> EvidenceFirstPipeline:
    """Bootstrap the integrated evidence-first analytical pipeline.

    Single entry point reaching the full chain (ingestion through
    Knowledge Filter plus the proposed representation). Analysis-only:
    no approval, authorization, execution, or vault mutation.
    """

    pipeline = EvidenceFirstPipeline()

    print("Reader Registry initialized.")

    print("Chunker Registry initialized.")

    print("Parser initialized.")

    print("Classifier initialized.")

    print("Pipeline initialized.")

    print("LivingAuthenticity Environment initialized successfully.")

    return pipeline


if __name__ == "__main__":
    main()
