class Cleaner:
    """
    Cleans raw text before chunking.
    """

    def clean(self, text: str) -> str:
        """
        Clean raw text.

        Currently returns the input unchanged.
        """
        return text