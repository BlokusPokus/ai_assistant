"""
Vector store implementation of the memory interface using Chroma or Qdrant.

📁 memory/vector_memory.py
Concrete memory class using vector DB (like Chroma or Qdrant).
Stores and retrieves user history, tool outputs, notes.
"""

from .interface import MemoryInterface


class VectorMemory(MemoryInterface):
    def __init__(self, client):
        """
        Initialize with vector DB client (Chroma/Qdrant).
        """
        self.client = client
        self.collection = client.get_or_create_collection("agent_memory")

    def query(self, query: str, k: int = 5):
        """
        Search memory for relevant context.
        """
        # Embed the query
        query_embedding = self.client.embed_text(query)

        # Search for similar vectors
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=k
        )

        return [
            {
                "content": r.content,
                "metadata": r.metadata
            }
            for r in results
        ]

    def add(self, content: str, metadata: dict):
        """
        Add a new memory record.
        """
        # Embed the content
        embedding = self.client.embed_text(content)

        # Store in vector DB
        self.collection.add(
            embeddings=[embedding],
            documents=[content],
            metadatas=[metadata]
        )
