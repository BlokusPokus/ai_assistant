import numpy as np
from client import MemoryDBClient, VectorMemory, MemoryRecord
from dotenv import load_dotenv


class DummyEmbedder:
    """
    Fake embedding model for testing purposes.
    Always returns the same fixed vector (for easy debugging).
    """

    def embed_text(self, text: str):
        return [1.0] * 10  # fixed-length dummy embedding


def run_test():
    print("🧪 Starting memory test...")

    # Use in-memory SQLite for testing
    db_url = "sqlite:///:memory:"
    embedder = DummyEmbedder()

    # Step 1: Initialize memory client and vector memory
    print("🛠️  Initializing client...")
    client = MemoryDBClient(db_url=db_url, embedding_model=embedder)
    memory = VectorMemory(client=client, user_id=42)

    # Step 2: Add a record
    content = "Hello, this is a test memory."
    metadata = {"source": "test"}
    print(f"➕ Adding record: {content}")
    memory.add(content=content, metadata=metadata)

    # Step 3: Query the memory
    query_text = "test"
    print(f"🔍 Querying with: {query_text}")
    results = memory.query(query=query_text, k=5)

    # Step 4: Output results
    print("📦 Results:")
    for r in results:
        print(f"  - ID: {r.id}, Content: {r.content}, Metadata: {r.meta_data}")

    print("✅ Test complete.")


if __name__ == "__main__":
    run_test()
