from src.living_authenticity.knowledge.ingestion.cleaning.normalizer import Normalizer


def test_normalizer_preserves_normal_text():
    normalizer = Normalizer()
    text = "Observation:\nPeople often lose the ability to enjoy calmness.\n"
    assert normalizer.normalize(text) == text


def test_normalizer_collapses_multiple_spaces():
    normalizer = Normalizer()
    text = "Word1    Word2\n"
    expected = "Word1 Word2\n"
    assert normalizer.normalize(text) == expected


def test_normalizer_collapses_many_spaces():
    normalizer = Normalizer()
    text = "A        B\n"
    expected = "A B\n"
    assert normalizer.normalize(text) == expected


def test_normalizer_preserves_single_spaces():
    normalizer = Normalizer()
    text = "A B C\n"
    assert normalizer.normalize(text) == text


def test_normalizer_preserves_meaning():
    normalizer = Normalizer()
    text = "Observation:\nPeople often lose the ability to enjoy calmness.\n"
    normalized = normalizer.normalize(text)
    assert "Observation:" in normalized
    assert "People often lose the ability to enjoy calmness." in normalized


def test_normalizer_handles_empty_input():
    normalizer = Normalizer()
    assert normalizer.normalize("") == ""


def test_normalizer_preserves_markdown_structure():
    normalizer = Normalizer()
    text = "# Heading\n\nParagraph with **bold** and *italic*.\n"
    normalized = normalizer.normalize(text)
    assert "# Heading" in normalized
    assert "**bold**" in normalized
    assert "*italic*" in normalized


def test_normalizer_preserves_leading_spaces():
    normalizer = Normalizer()
    text = "  indented line\n"
    assert normalizer.normalize(text) == text


def test_normalizer_preserves_line_structure():
    normalizer = Normalizer()
    text = "Line one.\nLine two.\nLine three.\n"
    assert normalizer.normalize(text) == text


def test_normalizer_preserves_persian_text():
    normalizer = Normalizer()
    text = "مشاهده:\nافرادی که در محیط‌های مملو از دغدغه رشد کرده‌اند.\n"
    normalized = normalizer.normalize(text)
    assert "مشاهده:" in normalized
    assert "افرادی که در محیط‌های مملو از دغدغه رشد کرده‌اند." in normalized


def test_normalizer_preserves_wikilinks_and_hashtags():
    normalizer = Normalizer()
    text = "Relations:\n[[Peace]]\n[[Survival]]\n\nTags:\n#peace\n#calmness\n"
    normalized = normalizer.normalize(text)
    assert "[[Peace]]" in normalized
    assert "[[Survival]]" in normalized
    assert "#peace" in normalized
    assert "#calmness" in normalized