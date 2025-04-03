"""
Vector store implementation of the memory interface using Chroma or Qdrant.

📁 memory/vector_memory.py
Concrete memory class using vector DB (like Chroma or Qdrant).
Stores and retrieves user history, tool outputs, notes.
"""

from .interface import MemoryInterface
from .client import MemoryDBClient


class Memory(MemoryInterface):
    def __init__(self, client: MemoryDBClient):
        """
        Initialize with memory DB client.
        """
        self.client = client

    def query(self, user_id: int, query: str, k: int):
        """Query the memory database."""
        return self.client.query_records(user_id, query, n_results=k)

    def add(self, user_id: int, content: str, metadata: dict):
        """Add content to the memory database."""
        self.client.add_record(user_id, content, metadata)
