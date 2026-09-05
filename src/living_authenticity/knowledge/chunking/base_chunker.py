from abc import ABC, abstractmethod


class BaseChunker(ABC):
    """
    Base class for all chunkers.

    A chunker divides cleaned text into a list of chunk strings.
    """

    @abstractmethod
    def split(self, text: str) -> list[str]:
        """
        Split cleaned text into chunk strings.
        """
