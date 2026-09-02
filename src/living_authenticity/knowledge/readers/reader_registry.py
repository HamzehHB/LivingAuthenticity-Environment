from pathlib import Path

from .markdown_reader import MarkdownReader
from .txt_reader import TXTReader


class ReaderRegistry:
    """
    Returns the correct reader based on file extension.
    """

    def __init__(self):

        self._readers = {
            ".txt": TXTReader(),
            ".md": MarkdownReader(),
        }

    def register(self, extension: str, reader):

        self._readers[extension.lower()] = reader

    def get(self, file_path: str):

        extension = Path(file_path).suffix.lower()

        if extension not in self._readers:

            raise ValueError(
                f"No reader registered for '{extension}'"
            )

        return self._readers[extension]