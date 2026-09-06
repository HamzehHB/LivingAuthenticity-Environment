from pathlib import Path


class MetadataExtractor:
    """
    Extracts file-level metadata for an ingested source file.
    """

    def extract(self, source: str):

        path = Path(source)

        return {
            "source": str(path),
            "file_name": path.name,
            "extension": path.suffix,
        }