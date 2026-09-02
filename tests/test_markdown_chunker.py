from src.living_authenticity.knowledge.chunking.markdown_chunker import (
    MarkdownChunker,
)


ENGLISH_NOTE = """
Observation:
People often lose the ability to enjoy calmness.

Relations:
[[Peace]]
[[Survival]]

Tags:
#peace
#mindfulness

Origin:
Personal observation

Questions:
How can calmness be relearned?
"""


def test_markdown_chunker_splits_labeled_sections():
    chunker = MarkdownChunker()
    sections = chunker.split(ENGLISH_NOTE)

    assert len(sections) >= 2
    assert any(section.startswith("Observation:") for section in sections)
    assert any(section.startswith("Relations:") for section in sections)
    assert any("[[Peace]]" in section for section in sections)
