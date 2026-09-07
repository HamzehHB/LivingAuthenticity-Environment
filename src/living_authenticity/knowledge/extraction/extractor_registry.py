from pathlib import Path

from .markdown_extractor import MarkdownKnowledgeExtractor
from .plain_text_extractor import PlainTextKnowledgeExtractor


class ExtractorRegistry:
    """Choose the appropriate knowledge-unit extractor by file extension."""

    def __init__(self):
        self._extractors = {
            ".md": MarkdownKnowledgeExtractor(),
            ".txt": PlainTextKnowledgeExtractor(),
        }

    def register(self, extension: str, extractor) -> None:
        self._extractors[extension.lower()] = extractor

    def get(self, file_path: str):
        extension = Path(file_path).suffix.lower()
        if extension not in self._extractors:
            raise ValueError(
                f"No knowledge unit extractor registered for '{extension}'"
            )
        return self._extractors[extension]
