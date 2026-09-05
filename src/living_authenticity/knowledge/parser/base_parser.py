from abc import ABC, abstractmethod

from .parsed_note import ParsedNote


class BaseParser(ABC):

    @abstractmethod
    def parse(self, text: str) -> ParsedNote:
        """
        Parse raw text into a structured ParsedNote.
        """
