from src.living_authenticity.knowledge.cleaning.cleaner import Cleaner


def test_cleaner_preserves_normal_text():
    cleaner = Cleaner()
    text = "Observation:\nPeople often lose the ability to enjoy calmness.\n"
    assert cleaner.clean(text) == text


def test_cleaner_normalizes_unicode_nfc():
    cleaner = Cleaner()
    # é as e + combining acute accent (NFD) -> precomposed é (NFC)
    nfd = "People o\u0301ften lose the ability."
    expected = "People \u00f3ften lose the ability."
    assert cleaner.clean(nfd) == expected


def test_cleaner_normalizes_crlf_line_endings():
    cleaner = Cleaner()
    text = "Line one.\r\nLine two.\r\n"
    expected = "Line one.\nLine two.\n"
    assert cleaner.clean(text) == expected


def test_cleaner_normalizes_cr_line_endings():
    cleaner = Cleaner()
    text = "Line one.\rLine two.\r"
    expected = "Line one.\nLine two.\n"
    assert cleaner.clean(text) == expected


def test_cleaner_removes_trailing_whitespace():
    cleaner = Cleaner()
    text = "Line one.   \nLine two.\n"
    expected = "Line one.\nLine two.\n"
    assert cleaner.clean(text) == expected


def test_cleaner_collapses_excessive_blank_lines():
    cleaner = Cleaner()
    text = "Paragraph one.\n\n\n\nParagraph two.\n"
    expected = "Paragraph one.\n\nParagraph two.\n"
    assert cleaner.clean(text) == expected


def test_cleaner_preserves_meaning():
    cleaner = Cleaner()
    text = "Observation:\nPeople often lose the ability to enjoy calmness.\n\nRelations:\n[[Peace]]\n"
    cleaned = cleaner.clean(text)
    assert "Observation:" in cleaned
    assert "People often lose the ability to enjoy calmness." in cleaned
    assert "[[Peace]]" in cleaned


def test_cleaner_handles_empty_input():
    cleaner = Cleaner()
    assert cleaner.clean("") == ""


def test_cleaner_handles_whitespace_only_input():
    cleaner = Cleaner()
    assert cleaner.clean("   \n\n   \n") == "\n\n"


def test_cleaner_preserves_markdown_structure():
    cleaner = Cleaner()
    text = "# Heading\n\nParagraph with **bold** and *italic*.\n\n- List item 1\n- List item 2\n"
    cleaned = cleaner.clean(text)
    assert "# Heading" in cleaned
    assert "**bold**" in cleaned
    assert "*italic*" in cleaned
    assert "- List item 1" in cleaned


def test_cleaner_preserves_wikilinks_and_hashtags():
    cleaner = Cleaner()
    text = "Observation:\nPeople often lose the ability.\n\nRelations:\n[[Peace]]\n[[Survival]]\n\nTags:\n#peace\n#calmness\n"
    cleaned = cleaner.clean(text)
    assert "[[Peace]]" in cleaned
    assert "[[Survival]]" in cleaned
    assert "#peace" in cleaned
    assert "#calmness" in cleaned


def test_cleaner_preserves_special_characters():
    cleaner = Cleaner()
    text = "Observation:\nPeople often lose the ability to enjoy calmness & peace.\n"
    cleaned = cleaner.clean(text)
    assert "&" in cleaned
    assert "calmness & peace" in cleaned