from dataclasses import dataclass, field


@dataclass
class ParsedNote:

    note_type: str

    title: str

    body: str

    relations: list[str] = field(default_factory=list)

    tags: list[str] = field(default_factory=list)

    additional_notes: str = ""

    open_questions: list[str] = field(default_factory=list)

    origin: str = ""

    status: str = ""

    conflicts: list[str] = field(default_factory=list)
