class Chunker:
    """
    Splits text into semantic chunks with paragraph overlap.
    """

    def __init__(
        self,
        max_chunk_size: int = 500,
        minimum_chunk_size: int = 120,
        overlap: int = 1,
    ):
        self.max_chunk_size = max_chunk_size
        self.minimum_chunk_size = minimum_chunk_size
        self.overlap = overlap

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

        current_chunk = []
        current_length = 0

        for paragraph in paragraphs:

            paragraph_length = len(paragraph)

            if paragraph_length > self.max_chunk_size:

                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))
                    current_chunk = []
                    current_length = 0

                remaining = paragraph

                while len(remaining) > self.max_chunk_size:

                    split_position = self._find_split_position(
                        remaining
                    )

                    first = remaining[:split_position].strip()
                    second = remaining[split_position:].strip()

                    if len(second) < self.minimum_chunk_size:
                        chunks.append(remaining)
                        remaining = ""
                        break

                    chunks.append(first)
                    remaining = second

                if remaining:
                    chunks.append(remaining)

                continue

            if (
                current_length + paragraph_length
                > self.max_chunk_size
            ):

                chunks.append("\n\n".join(current_chunk))

                current_chunk = current_chunk[-self.overlap :]

                current_length = sum(
                    len(p)
                    for p in current_chunk
                )

            current_chunk.append(paragraph)

            current_length += paragraph_length

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks