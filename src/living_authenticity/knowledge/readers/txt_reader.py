from pathlib import Path

from .base_reader import BaseReader


class TXTReader(BaseReader):
    """
    Reader for plain text files.
    """

    def read(self, file_path: str) -> str:
        path = Path(file_path)

        with path.open("r", encoding="utf-8") as file:
            return file.read()