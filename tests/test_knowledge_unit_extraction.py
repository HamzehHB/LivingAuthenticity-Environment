from pathlib import Path

import pytest

from src.living_authenticity.knowledge.cleaning.cleaner import Cleaner
from src.living_authenticity.knowledge.cleaning.normalizer import Normalizer
from src.living_authenticity.knowledge.extraction import (
    ExtractorRegistry,
    KnowledgeUnit,
    MarkdownKnowledgeExtractor,
    PlainTextKnowledgeExtractor,
    make_unit_id,
)
from src.living_authenticity.knowledge.extraction.base_extractor import (
    KnowledgeUnitExtractor,
)
from src.living_authenticity.knowledge.parser.obsidian_parser import ObsidianParser


def _ext():
    return MarkdownKnowledgeExtractor()


def _parser():
    return ObsidianParser()


def _parsed(text):
    p = _parser()
    parsed = p.parse(text)
    return parsed, p


class TestEmptyAndWhitespace:
    def test_empty_input_returns_zero_units(self):
        ext = _ext()
        assert ext.extract("s.md", "", "", "", None, None) == []

    def test_whitespace_only_returns_zero_units(self):
        ext = _ext()
        assert ext.extract("s.md", "   \n\n  ", "   \n\n  ", "   \n\n  ", None, None) == []

    def test_whitespace_cleaned_to_empty_returns_zero_units(self):
        ext = _ext()
        cleaned = Cleaner().clean("   \n\n   \n")
        assert ext.extract("s.md", "   \n\n   \n", cleaned, cleaned, None, None) == []


class TestSingleUnit:
    def test_one_clear_idea_is_one_unit(self):
        ext = _ext()
        text = "Observation:\nPeople often lose the ability to enjoy calmness.\n"
        parsed, parser = _parsed(text)
        units = ext.extract("s.md", text, text, text, parsed, parser)
        assert len(units) == 1
        assert "People often lose the ability" in units[0].cleaned_text
        assert units[0].boundary_basis == "labeled_section"

    def test_short_input_one_unit(self):
        ext = _ext()
        text = "Observation:\nShort idea.\n"
        parsed, parser = _parsed(text)
        units = ext.extract("s.md", text, text, text, parsed, parser)
        assert len(units) == 1


class TestMultipleUnits:
    def test_two_clearly_independent_sections_two_units(self):
        ext = _ext()
        text = "Observation:\nFirst independent idea here.\n\nConcept:\nSecond different idea.\n"
        parsed, parser = _parsed(text)
        units = ext.extract("s.md", text, text, text, parsed, parser)
        assert len(units) == 2
        assert "First independent" in units[0].cleaned_text
        assert "Second different" in units[1].cleaned_text

    def test_metadata_sections_excluded(self):
        ext = _ext()
        text = (
            "Observation:\nReal knowledge here.\n\n"
            "Relations:\n[[Peace]]\n\n"
            "Tags:\n#peace\n"
        )
        parsed, parser = _parsed(text)
        units = ext.extract("s.md", text, text, text, parsed, parser)
        assert len(units) == 1
        assert "Real knowledge" in units[0].cleaned_text


class TestRelatedSentencesPreserved:
    def test_closely_related_sentences_stay_together(self):
        ext = _ext()
        text = (
            "Observation:\n"
            "People often lose the ability to enjoy calmness. "
            "This happens especially in stressful environments.\n"
        )
        parsed, parser = _parsed(text)
        units = ext.extract("s.md", text, text, text, parsed, parser)
        assert len(units) == 1
        assert "stressful environments" in units[0].cleaned_text

    def test_dependent_list_items_stay_together(self):
        ext = _ext()
        text = (
            "Examples:\n"
            "- depends on stem\n"
            "- also depends\n"
        )
        parsed, parser = _parsed(text)
        units = ext.extract("s.md", text, text, text, parsed, parser)
        assert len(units) == 1
        assert units[0].boundary_basis == "labeled_section"


class TestIndependentListItems:
    def test_independent_list_items_split(self):
        ext = _ext()
        text = (
            "Observation:\n"
            "First complete independent sentence here.\n"
            "Second complete independent sentence here.\n"
            "Third complete independent sentence here.\n"
        )
        parsed, parser = _parsed(text)
        units = ext.extract("s.md", text, text, text, parsed, parser)
        assert len(units) == 3
        assert units[0].boundary_basis == "independent_list_items"


class TestMarkdownHeadings:
    def test_multiple_sub_ideas_in_section_split(self):
        ext = _ext()
        text = (
            "Observation:\nFirst paragraph of the observation.\n\n"
            "Second paragraph with a different angle.\n"
        )
        parsed, parser = _parsed(text)
        units = ext.extract("s.md", text, text, text, parsed, parser)
        assert len(units) == 2
        assert units[0].boundary_basis == "section_sub_idea"


class TestUnicodeAndPersian:
    def test_persian_text_extracts(self):
        ext = _ext()
        text = "مشاهده مطرح‌شده:\nافرادی که در محیط‌های مملو از دغدغه رشد کرده‌اند.\n"
        parsed, parser = _parsed(text)
        units = ext.extract("s.md", text, text, text, parsed, parser)
        assert len(units) == 1
        assert "دغدغه" in units[0].cleaned_text

    def test_persian_multi_section(self):
        ext = _ext()
        text = (
            "مشاهده مطرح‌شده:\nاولین مشاهده مستقل.\n\n"
            "مفاهیم:\nمفهوم دوم کاملاً متفاوت.\n"
        )
        parsed, parser = _parsed(text)
        units = ext.extract("s.md", text, text, text, parsed, parser)
        assert len(units) == 2




class TestMeaningAndRepresentation:
    def test_meaning_preserved(self):
        ext = _ext()
        text = "Observation:\nPeople often lose the ability to enjoy calmness.\n"
        parsed, parser = _parsed(text)
        units = ext.extract("s.md", text, text, text, parsed, parser)
        assert units[0].meaning == units[0].cleaned_text

    def test_proposed_type_unresolved(self):
        ext = _ext()
        text = "Observation:\nSome knowledge.\n"
        parsed, parser = _parsed(text)
        units = ext.extract("s.md", text, text, text, parsed, parser)
        assert all(u.proposed_type == "" for u in units)

    def test_normalized_representation_retained(self):
        ext = _ext()
        original = "Observation:   \nPeople often    lose the ability.\n"
        cleaned = Cleaner().clean(original)
        normalized = Normalizer().normalize(cleaned)
        parsed, parser = _parsed(cleaned)
        units = ext.extract("s.md", original, cleaned, normalized, parsed, parser)
        assert len(units) == 1
        assert "People often lose the ability." in units[0].normalized_text


class TestDeterministicIds:
    def test_same_input_same_ids(self):
        ext = _ext()
        text = "Observation:\nStable knowledge.\n"
        parsed, parser = _parsed(text)
        ids1 = [u.id for u in ext.extract("s.md", text, text, text, parsed, parser)]
        ids2 = [u.id for u in ext.extract("s.md", text, text, text, parsed, parser)]
        assert ids1 == ids2

    def test_different_source_different_ids(self):
        text = "Observation:\nStable knowledge.\n"
        parsed, parser = _parsed(text)
        ext = _ext()
        ids1 = [u.id for u in ext.extract("a.md", text, text, text, parsed, parser)]
        ids2 = [u.id for u in ext.extract("b.md", text, text, text, parsed, parser)]
        assert ids1 != ids2

    def test_make_unit_id_deterministic(self):
        a = make_unit_id("s.md", 0, "hello")
        b = make_unit_id("s.md", 0, "hello")
        assert a == b
        assert a.startswith("ku-")


class TestPlainTextExtractor:
    def test_plain_text_paragraphs(self):
        ext = PlainTextKnowledgeExtractor()
        text = "First paragraph of knowledge.\n\nSecond paragraph of knowledge.\n"
        units = ext.extract("s.txt", text, text, text, None, None)
        assert len(units) == 2

    def test_plain_text_empty(self):
        ext = PlainTextKnowledgeExtractor()
        assert ext.extract("s.txt", "", "", "", None, None) == []

    def test_plain_text_independent_list(self):
        ext = PlainTextKnowledgeExtractor()
        text = "First complete sentence.\nSecond complete sentence.\n"
        units = ext.extract("s.txt", text, text, text, None, None)
        assert len(units) == 2


class TestExtractorRegistry:
    def test_registry_returns_markdown_for_md(self):
        reg = ExtractorRegistry()
        ext = reg.get("note.md")
        assert isinstance(ext, MarkdownKnowledgeExtractor)

    def test_registry_returns_plain_for_txt(self):
        reg = ExtractorRegistry()
        ext = reg.get("note.txt")
        assert isinstance(ext, PlainTextKnowledgeExtractor)

    def test_registry_rejects_unknown(self):
        reg = ExtractorRegistry()
        with pytest.raises(ValueError, match="No knowledge unit extractor"):
            reg.get("file.pdf")

    def test_registry_accepts_custom(self):
        reg = ExtractorRegistry()
        custom = PlainTextKnowledgeExtractor()
        reg.register(".custom", custom)
        assert reg.get("file.CUSTOM") is custom


class TestSecurity:
    def test_no_eval_or_exec(self):
        ext = _ext()
        text = "Observation:\n__import__('os').system('echo pwned')\n"
        parsed, parser = _parsed(text)
        units = ext.extract("s.md", text, text, text, parsed, parser)
        assert len(units) == 1
        assert "__import__" in units[0].original_text

class TestProvenance:
    def test_unit_retains_source(self):
        ext = _ext()
        text = "Observation:\nSome knowledge.\n"
        parsed, parser = _parsed(text)
        units = ext.extract("path/to/note.md", text, text, text, parsed, parser)
        assert all(u.source == "path/to/note.md" for u in units)

    def test_deterministic_ordering(self):
        ext = _ext()
        text = "Observation:\nA.\n\nConcept:\nB.\n\nResearch:\nC.\n"
        parsed, parser = _parsed(text)
        units = ext.extract("s.md", text, text, text, parsed, parser)
        positions = [u.position for u in units]
        assert positions == sorted(positions)
        assert len(set(positions)) == len(positions)

    def test_context_preserved(self):
        ext = _ext()
        text = "Observation:\nBody here.\n"
        parsed, parser = _parsed(text)
        units = ext.extract("s.md", text, text, text, parsed, parser)
        assert len(units) == 1
        assert units[0].context == "Observation"
        assert "Body here." in units[0].cleaned_text
