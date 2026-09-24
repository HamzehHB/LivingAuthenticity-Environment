from abc import ABC, abstractmethod


class BaseReader(ABC):
    """
    Base class for all knowledge readers.
    """

    @abstractmethod
    def read(self, file_path: str) -> str:
        """
        Read a file and return its raw text.
        """
        pass