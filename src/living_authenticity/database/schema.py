import pyarrow as pa

VECTOR_DIMENSION = 1024

KNOWLEDGE_VECTOR_SCHEMA = pa.schema([
    pa.field("id", pa.string()),
    pa.field("text", pa.string()),
    pa.field("embedding", pa.list_(pa.float32(), VECTOR_DIMENSION)),
])