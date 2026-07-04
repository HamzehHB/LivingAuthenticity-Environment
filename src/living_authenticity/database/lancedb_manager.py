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