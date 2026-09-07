from src.living_authenticity.knowledge.parser.obsidian_parser import ObsidianParser
from src.living_authenticity.knowledge.parser.note_types import NoteType


ENGLISH_NOTE = """
Observation:
People often lose the ability to enjoy calmness.

Relations:
[[Peace]]
[[Survival]]

Tags:
#peace

Origin:
Personal observation.

Questions:
How can calmness be relearned?
"""

PERSIAN_NOTE = """
مشاهده مطرح‌شده:
افرادی که در محیط‌های مملو از دغدغه رشد کرده‌اند ممکن است توانایی تجربه آرامش را از دست بدهند.

نمونه‌های مطرح‌شده:
- تجربه آرامش با احساس اتلاف وقت اشتباه گرفته می‌شود.

ارتباطات:
[[سیستم بقا]]
[[سیستم آرامش]]

Origin:
مشاهده مبتنی بر تجربه شخصی

وضعیت:
مستقل

تعارض با مدل فعلی:
ندارد

سؤال‌های باز:
چگونه می‌توان توانایی تجربه آرامش را بازآموخت؟
"""


def test_parse_english_labeled_note():
    parsed = ObsidianParser().parse(ENGLISH_NOTE)

    assert parsed.note_type == NoteType.OBSERVATION.value
    assert "People often lose the ability to enjoy calmness." in parsed.body
    assert parsed.relations == ["Peace", "Survival"]
    assert parsed.tags == ["peace"]
    assert parsed.origin == "Personal observation."
    assert parsed.open_questions == ["How can calmness be relearned?"]
    assert parsed.title.startswith("People often lose")


def test_parse_persian_labeled_note():
    parsed = ObsidianParser().parse(PERSIAN_NOTE)

    assert parsed.note_type == NoteType.OBSERVATION.value
    assert "آرامش" in parsed.body
    assert "سیستم بقا" in parsed.relations
    assert "سیستم آرامش" in parsed.relations
    assert parsed.status == "مستقل"
    assert parsed.conflicts == ["ندارد"]
    assert parsed.additional_notes
    assert parsed.open_questions


def test_parse_empty_input():
    parsed = ObsidianParser().parse("")

    assert parsed.note_type == ""
    assert parsed.body == ""
    assert parsed.relations == []
    assert parsed.tags == []
    assert parsed.title == ""


def test_parse_whitespace_only_input():
    parsed = ObsidianParser().parse("   \n\n   \n")

    assert parsed.note_type == ""
    assert parsed.body == ""
    assert parsed.relations == []
    assert parsed.tags == []


def test_parse_malformed_input_without_labels():
    text = "Just some random text without any labels."
    parsed = ObsidianParser().parse(text)

    assert parsed.note_type == ""
    assert text in parsed.body
    assert parsed.relations == []
    assert parsed.tags == []


def test_parse_preserves_unicode_in_body():
    text = "Observation:\nPeople o\u0301ften lose the ability.\n"
    parsed = ObsidianParser().parse(text)

    assert parsed.note_type == NoteType.OBSERVATION.value
    assert "People o\u0301ften lose the ability." in parsed.body
    assert not hasattr(NoteType, "INBOX")
    assert {member.value for member in NoteType} == {
        "Core",
        "Concept",
        "Observation",
        "Experience",
        "Research",
        "Method",
        "Source",
        "Meta",
        "Archive",
    }
