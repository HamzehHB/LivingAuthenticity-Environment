from pathlib import Path

from .markdown_chunker import MarkdownChunker
from .paragraph_chunker import ParagraphChunker


class ChunkerRegistry:
    """
    Chooses the appropriate chunker.
    """

    def __init__(self):

        self._chunkers = {
            ".md": MarkdownChunker(),
            ".txt": ParagraphChunker(),
        }

    def register(self, extension: str, chunker):

        self._chunkers[extension.lower()] = chunker

    def get(self, file_path: str):

        extension = Path(file_path).suffix.lower()

        return self._chunkers.get(
            extension,
            ParagraphChunker(),
        )