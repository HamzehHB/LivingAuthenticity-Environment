from .base_chunker import BaseChunker


class ParagraphChunker(BaseChunker):
    """
    Simple paragraph-based chunker.
    """

    def split(self, text: str) -> list[str]:

        paragraphs = [
            p.strip()
            for p in text.split("\n\n")
            if p.strip()
        ]

        return paragraphs