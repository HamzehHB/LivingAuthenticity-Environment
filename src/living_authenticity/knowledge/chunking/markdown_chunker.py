import re

from .base_chunker import BaseChunker


class MarkdownChunker(BaseChunker):
    """
    Chunker مخصوص Obsidian Markdown.

    ابتدا فایل را به Sectionهای منطقی تقسیم می‌کند.
    """

    SECTION_PATTERN = re.compile(
        r"(?=^(?:[A-Za-zآ-ی ]+):)",
        re.MULTILINE,
    )

    def split(self, text: str):

        sections = [
            section.strip()
            for section in self.SECTION_PATTERN.split(text)
            if section.strip()
        ]

        return sections