from abc import ABC, abstractmethod


class BaseChunker(ABC):
    """
    Base class for all chunkers.
    """

    @abstractmethod
    def split(self, text: str):
        pass