from src.living_authenticity.knowledge.chunking.chunker import Chunker


def main():

    text = """
Living Authenticity is not simply being yourself. It is the continuous integration of identity, meaning, and lived experience through authentic action. Human beings constantly reconstruct themselves through reflection and action. Authenticity is therefore never static.

Living Authenticity is not simply being yourself. It is the continuous integration of identity, meaning, and lived experience through authentic action. Human beings constantly reconstruct themselves through reflection and action. Authenticity is therefore never static.

Living Authenticity is not simply being yourself. It is the continuous integration of identity, meaning, and lived experience through authentic action. Human beings constantly reconstruct themselves through reflection and action. Authenticity is therefore never static.

Living Authenticity is not simply being yourself. It is the continuous integration of identity, meaning, and lived experience through authentic action. Human beings constantly reconstruct themselves through reflection and action. Authenticity is therefore never static.

Living Authenticity is not simply being yourself. It is the continuous integration of identity, meaning, and lived experience through authentic action. Human beings constantly reconstruct themselves through reflection and action. Authenticity is therefore never static.
"""

    chunker = Chunker(
        max_chunk_size=250,
        minimum_chunk_size=120,
    )

    chunks = chunker.split(text)

    print(f"\nChunks: {len(chunks)}\n")

    for i, chunk in enumerate(chunks, start=1):

        print(f"Chunk {i}")
        print("-" * 40)
        print(f"Length: {len(chunk)}")
        print(chunk)
        print()


if __name__ == "__main__":
    main()