from src.living_authenticity.knowledge.chunking.chunker import Chunker


def main():

    text = """

Paragraph One.

Paragraph Two.

Paragraph Three.

Paragraph Four.

Paragraph Five.

Paragraph Six.

Paragraph Seven.

Paragraph Eight.

"""

    chunker = Chunker(
        max_chunk_size=60,
        overlap=1,
    )

    chunks = chunker.split(text)

    print(f"\nChunks: {len(chunks)}\n")

    for i, chunk in enumerate(chunks, start=1):

        print(f"Chunk {i}")
        print("-" * 40)
        print(chunk)
        print()


if __name__ == "__main__":
    main()