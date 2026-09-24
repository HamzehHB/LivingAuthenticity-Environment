import re

from .base_parser import BaseParser
from .note_types import NoteType
from .parsed_note import ParsedNote


WIKILINK_PATTERN = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
HASHTAG_PATTERN = re.compile(r"(?<!\w)#([\wآ-ی-]+)", re.UNICODE)
LABEL_LINE_PATTERN = re.compile(
    r"^(?P<label>[^\n:]{1,80}):(?:[ \t]*(?P<rest>.*))?$",
    re.MULTILINE,
)


def _normalize_label(label: str) -> str:
    cleaned = label.replace("\u200c", " ").strip().lower()
    return re.sub(r"\s+", " ", cleaned)


_TYPE_BY_LABEL = {
    "observation": NoteType.OBSERVATION,
    "مشاهده": NoteType.OBSERVATION,
    "مشاهده مطرح شده": NoteType.OBSERVATION,
    "concept": NoteType.CONCEPT,
    "مفاهیم": NoteType.CONCEPT,
    "experience": NoteType.EXPERIENCE,
    "تجربه": NoteType.EXPERIENCE,
    "research": NoteType.RESEARCH,
    "پژوهش": NoteType.RESEARCH,
    "method": NoteType.METHOD,
    "روش": NoteType.METHOD,
    "source": NoteType.SOURCE,
    "منبع": NoteType.SOURCE,
    "core": NoteType.CORE,
    "meta": NoteType.META,
    "archive": NoteType.ARCHIVE,
}

_BODY_LABELS = {
    "observation",
    "مشاهده",
    "مشاهده مطرح شده",
    "body",
}

_RELATION_LABELS = {
    "relations",
    "ارتباطات",
}

_TAG_LABELS = {
    "tags",
    "تگ",
    "برچسب",
}

_ORIGIN_LABELS = {
    "origin",
}

_QUESTION_LABELS = {
    "questions",
    "سؤال های باز",
    "سوال های باز",
}

_STATUS_LABELS = {
    "status",
    "وضعیت",
}

_CONFLICT_LABELS = {
    "conflict",
    "تعارض",
    "تعارض با مدل فعلی",
}

_ADDITIONAL_LABELS = {
    "examples",
    "نمونه های مطرح شده",
}


def _non_empty_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


class ObsidianParser(BaseParser):
    """
    Minimal labeled-section parser for fixture notes.

    Does not write files or invent knowledge identifiers.
    """

    def parse(self, text: str) -> ParsedNote:
        sections = self._split_sections(text)

        body_parts: list[str] = []
        additional_parts: list[str] = []
        relations: list[str] = []
        tags: list[str] = []
        open_questions: list[str] = []
        conflicts: list[str] = []
        origin = ""
        status = ""
        note_type = ""

        unlabeled_prefix = sections[0][1] if sections and sections[0][0] == "" else ""

        for label, content in sections:
            if label == "":
                continue

            key = _normalize_label(label)
            mapped_type = _TYPE_BY_LABEL.get(key)
            if mapped_type is not None and not note_type:
                note_type = mapped_type.value

            if key in _BODY_LABELS:
                body_parts.append(content.strip())
            elif key in _RELATION_LABELS:
                relations.extend(self._extract_wikilinks(content))
            elif key in _TAG_LABELS:
                tags.extend(self._extract_tags(content))
            elif key in _ORIGIN_LABELS:
                origin = content.strip()
            elif key in _QUESTION_LABELS:
                open_questions.extend(_non_empty_lines(content))
            elif key in _STATUS_LABELS:
                status = content.strip()
            elif key in _CONFLICT_LABELS:
                conflicts.extend(_non_empty_lines(content))
            elif key in _ADDITIONAL_LABELS:
                additional_parts.append(content.strip())
            elif mapped_type is not None:
                body_parts.append(content.strip())

        if not relations:
            relations = self._extract_wikilinks(text)

        if not tags:
            tags = self._extract_tags(text)

        body = "\n\n".join(part for part in body_parts if part)
        if not body and unlabeled_prefix.strip():
            body = unlabeled_prefix.strip()

        additional_notes = "\n\n".join(part for part in additional_parts if part)
        title = self._title_from_body(body)

        return ParsedNote(
            note_type=note_type,
            title=title,
            body=body,
            relations=self._unique(relations),
            tags=self._unique(tags),
            additional_notes=additional_notes,
            open_questions=open_questions,
            origin=origin,
            status=status,
            conflicts=conflicts,
        )

    def _split_sections(self, text: str) -> list[tuple[str, str]]:
        matches = list(LABEL_LINE_PATTERN.finditer(text))
        if not matches:
            return [("", text)]

        sections: list[tuple[str, str]] = []
        first = matches[0]
        if first.start() > 0:
            prefix = text[: first.start()]
            if prefix.strip():
                sections.append(("", prefix))

        for index, match in enumerate(matches):
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            rest = match.group("rest") or ""
            following = text[match.end() : end]
            content = rest + (("\n" + following) if following else "")
            sections.append((match.group("label").strip(), content))
        return sections

    def section_boundaries(self, text: str) -> list[tuple[str, int, int]]:
        """Return labeled sections as ``(label, start, end)`` char spans.

        ``start`` points at the first character of the label line and ``end``
        points just past the last character of that section's content. The
        returned spans are therefore suitable for slicing the text (and any
        representation that preserves character positions relative to it) into
        per-section chunks.

        Sections without a leading label are returned with an empty label.
        """
        matches = list(LABEL_LINE_PATTERN.finditer(text))
        if not matches:
            return [("", 0, len(text))]

        boundaries: list[tuple[str, int, int]] = []
        first = matches[0]
        if first.start() > 0:
            prefix = text[: first.start()]
            if prefix.strip():
                boundaries.append(("", 0, first.start()))

        for index, match in enumerate(matches):
            start = match.start()
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            boundaries.append((match.group("label").strip(), start, end))

        return boundaries

    def _extract_wikilinks(self, text: str) -> list[str]:
        return [match.strip() for match in WIKILINK_PATTERN.findall(text)]

    def _extract_tags(self, text: str) -> list[str]:
        return [match.strip() for match in HASHTAG_PATTERN.findall(text)]

    def _title_from_body(self, body: str) -> str:
        for line in body.splitlines():
            stripped = line.strip().lstrip("#").strip()
            if stripped:
                return stripped
        return ""

    def _unique(self, values: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for value in values:
            if value not in seen:
                seen.add(value)
                result.append(value)
        return result
