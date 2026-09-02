from .base_chunker import BaseChunker


class ParagraphChunker(BaseChunker):
    """
    Chunker ساده بر اساس پاراگراف.
    """

    def split(self, text: str):

        paragraphs = [
            p.strip()
            for p in text.split("\n\n")
            if p.strip()
        ]

        return paragraphs