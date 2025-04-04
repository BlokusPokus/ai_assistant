import os
from client import MemoryDBClient, VectorMemory


class DummyEmbedder:
    def embed_text(self, text):
        return [0.1 * i for i in range(10)]  # simple deterministic vector


def run_real_db_test():
    print("🔧 Connecting to real database...")

    # Replace with your real PostgreSQL connection string
    DB_URL = os.getenv(
        "REAL_DB_URL") or "postgresql://ianleblanc:password@localhost:5432/postgres"

    client = MemoryDBClient(db_url=DB_URL, embedding_model=DummyEmbedder())
    memory = VectorMemory(client=client, user_id=123)

    content = "This is a test memory entry for the real DB."
    # Renamed from embedding to metadata
    metadata = {"test": True, "source": "unit_test"}

    print("➕ Adding record to memory_chunks...")
    # Removed embedding argument
    memory.add(content=content, metadata=metadata)

    print("🔍 Querying memory_chunks...")
    results = memory.query(query="test", k=5)

    print("✅ Results:")
    for r in results:
        print(f" - id: {r.id}, content: {r.content}, embedding: {r.embedding}")


if __name__ == "__main__":
    run_real_db_test()
