import re


class Normalizer:
    """
    Normalizes cleaned text representation.

    Normalization further refines the cleaned representation without
    altering substantive meaning:
    - Collapse multiple spaces within lines to one
    """

    def normalize(self, text: str) -> str:
        """
        Normalize cleaned text.

        Collapses runs of multiple spaces into a single space
        within each line, preserving line structure and leading
        indentation.
        """
        lines = [re.sub(r"(?<=\S) {2,}", " ", line) for line in text.split("\n")]
        return "\n".join(lines)