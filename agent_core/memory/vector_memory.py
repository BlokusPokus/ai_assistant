"""
Vector store implementation of the memory interface using Chroma or Qdrant.

📁 memory/vector_memory.py
Concrete memory class using vector DB (like Chroma or Qdrant).
Stores and retrieves user history, tool outputs, notes.
"""

from .interface import MemoryInterface


class VectorMemory(MemoryInterface):
    def __init__(self, client):
        self.client = client

    def query(self, query: str, k: int = 5):
        # Embed query and perform similarity search
        pass

    def add(self, content: str, metadata: dict):
        # Embed content and store in vector DB
        pass
