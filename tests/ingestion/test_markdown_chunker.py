from src.living_authenticity.knowledge.ingestion.chunking.markdown_chunker import (
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

PERSIAN_NOTE = (
    "مشاهده مطرح\u200cشده:\n"
    "افرادی که در محیط های مملو از دغدغه رشد کرده اند ممکن است\n"
    "توانایی تجربه آرامش را از دست بدهند.\n"
    "\n"
    "نمونه\u200cهای مطرح\u200cشده:\n"
    "- تجربه آرامش با احساس اتلاف وقت اشتباه گرفته می شود.\n"
    "\n"
    "ارتباطات:\n"
    "[[سیستم بقا]]\n"
    "[[سیستم آرامش]]\n"
)


def test_markdown_chunker_splits_labeled_sections():
    chunker = MarkdownChunker()
    sections = chunker.split(ENGLISH_NOTE)

    assert len(sections) >= 2
    assert any(section.startswith("Observation:") for section in sections)
    assert any(section.startswith("Relations:") for section in sections)
    assert any("[[Peace]]" in section for section in sections)


def test_markdown_chunker_supports_persian_zwnj_labels():
    assert "\u200c" in PERSIAN_NOTE

    sections = MarkdownChunker().split(PERSIAN_NOTE)

    assert len(sections) == 3
    assert sections[0].startswith("مشاهده مطرح\u200cشده:")
    assert sections[1].startswith("نمونه\u200cهای مطرح\u200cشده:")
    assert sections[2].startswith("ارتباطات:")
    assert "[[سیستم بقا]]" in sections[2]


def test_markdown_chunker_keeps_url_lines_inside_sections():
    note = (
        "Observation:\n"
        "Reference material is available at https://example.com today.\n"
        "\n"
        "Origin:\n"
        "Personal observation.\n"
    )

    sections = MarkdownChunker().split(note)

    assert len(sections) == 2
    assert "https://example.com" in sections[0]
    assert sections[1].startswith("Origin:")


def test_markdown_chunker_does_not_split_on_bare_url_lines():
    note = (
        "Origin:\n"
        "https://example.com/source\n"
        "Personal observation.\n"
    )

    sections = MarkdownChunker().split(note)

    assert len(sections) == 1
    assert "https://example.com/source" in sections[0]


def test_markdown_chunker_does_not_split_on_mid_line_colons():
    note = (
        "Observation:\n"
        "Note: this inline sentence must stay inside its own section.\n"
    )

    sections = MarkdownChunker().split(note)

    assert len(sections) == 1
    assert "Note: this inline sentence" in sections[0]
