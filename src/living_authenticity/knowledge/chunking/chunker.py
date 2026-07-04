class Chunker:
    """
    Splits text into semantic chunks.
    """

    def __init__(
        self,
        max_chunk_size: int = 500,
        minimum_chunk_size: int = 120,
    ):
        self.max_chunk_size = max_chunk_size
        self.minimum_chunk_size = minimum_chunk_size

    def _find_split_position(self, text: str):

        if len(text) <= self.max_chunk_size:
            return len(text)

        search_area = text[: self.max_chunk_size]

        sentence_marks = [
            ".",
            "!",
            "?",
            "؟",
            "؛",
            ":",
        ]

        last_position = -1

        for mark in sentence_marks:

            position = search_area.rfind(mark)

            if position > last_position:
                last_position = position

        if last_position != -1:
            return last_position + 1

        newline = search_area.rfind("\n")

        if newline != -1:
            return newline

        space = search_area.rfind(" ")

        if space != -1:
            return space

        return self.max_chunk_size

    def split(self, text: str):

        paragraphs = [
            p.strip()
            for p in text.split("\n\n")
            if p.strip()
        ]

        chunks = []

        for paragraph in paragraphs:

            remaining = paragraph

            while len(remaining) > self.max_chunk_size:

                split_position = self._find_split_position(
                    remaining
                )

                first_part = remaining[:split_position].strip()
                second_part = remaining[split_position:].strip()

                # اگر بخش دوم خیلی کوچک است
                # اصلاً Split نکن.
                if len(second_part) < self.minimum_chunk_size:

                    chunks.append(remaining)
                    remaining = ""
                    break

                chunks.append(first_part)

                remaining = second_part

            if remaining:
                chunks.append(remaining)

        return chunks