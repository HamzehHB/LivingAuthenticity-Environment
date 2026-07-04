import uuid

import lancedb

from Config.settings import PATHS
from src.living_authenticity.database.schema import KNOWLEDGE_VECTOR_SCHEMA


class LanceDBManager:
    def __init__(self):
        db_path = PATHS["vector_db"]["lancedb"]
        self.db = lancedb.connect(db_path)

    def create_knowledge_vector_table(self):
        return self.db.create_table(
            "knowledge_vectors",
            schema=KNOWLEDGE_VECTOR_SCHEMA,
            exist_ok=True
        )

    def get_table(self):
        return self.db.open_table("knowledge_vectors")

    def store(self, text: str, embedding):
        table = self.get_table()

        table.add([
            {
                "id": str(uuid.uuid4()),
                "text": text,
                "embedding": embedding.tolist()
            }
        ])

    def show_all(self):
        table = self.get_table()
        return table.to_arrow().to_pylist()