class IngestionPipeline:
    """
    Coordinates the complete knowledge ingestion pipeline.
    """

    def __init__(
        self,
        reader,
        cleaner,
        chunker,
        metadata_extractor,
        embedding_service,
        database,
    ):
        self.reader = reader
        self.cleaner = cleaner
        self.chunker = chunker
        self.metadata_extractor = metadata_extractor
        self.embedding_service = embedding_service
        self.database = database

    def ingest(self, file_path: str):

        raw_text = self.reader.read(file_path)

        cleaned_text = self.cleaner.clean(raw_text)

        chunks = self.chunker.split(cleaned_text)

        for chunk in chunks:

            metadata = self.metadata_extractor.extract(file_path)

            embedding = self.embedding_service.embed(chunk)

            self.database.store(
                text=chunk,
                embedding=embedding,
                metadata=metadata,
            )

        return len(chunks)