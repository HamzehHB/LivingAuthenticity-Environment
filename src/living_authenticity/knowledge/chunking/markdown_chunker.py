import re

from .base_chunker import BaseChunker


class MarkdownChunker(BaseChunker):
    """
    Chunker مخصوص Obsidian Markdown.

    فایل را به Sectionهای منطقی تقسیم می کند.

    A section starts at a label line:

    * the line begins with a Latin or Persian letter,
    * continues with letters, spaces, or the Persian ZWNJ (U+200C),
    * and ends with a colon and nothing else.

    Inline colons never start a section, so URLs such as
    ``https://example.com`` and sentences like ``Note: ...`` stay
    inside the section they belong to.
    """

    SECTION_PATTERN = re.compile(
        r"(?=^[A-Za-zآ-ی][A-Za-zآ-ی \u200c]{0,79}:\s*$)",
        re.MULTILINE,
    )

    def split(self, text: str) -> list[str]:

        sections = [
            section.strip()
            for section in self.SECTION_PATTERN.split(text)
            if section.strip()
        ]

        return sections
