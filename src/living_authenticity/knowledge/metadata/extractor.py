from pathlib import Path


class MetadataExtractor:
    """
    Extracts metadata for each chunk.
    """

    def extract(self, source: str):

        path = Path(source)

        return {
            "source": str(path),
            "file_name": path.name,
            "extension": path.suffix,
        }