import lancedb

from Config.settings import PATHS

class LanceDBManager:
    def __init__(self):
        db_path = PATHS["vector_db"]["lancedb"]
        self.db = lancedb.connect(db_path)

    def get_database(self):
        return self.db