class Chunker:
    """
    Splits text into chunks.
    """

    def split(self, text: str):
        """
        Split text into chunks.

        Currently returns the whole text as a single chunk.
        """
        return [text]