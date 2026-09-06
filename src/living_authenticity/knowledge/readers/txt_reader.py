from pathlib import Path

from .base_reader import BaseReader


class TXTReader(BaseReader):
    """
    Reader for plain text files (UTF-8, with or without BOM).
    """

    def read(self, file_path: str) -> str:
        path = Path(file_path)

        with path.open("r", encoding="utf-8-sig") as file:
            return file.read()