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


def test_inbox_is_not_a_knowledge_type():
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
