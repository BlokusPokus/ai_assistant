"""
Vector database client interfaces and implementations.
"""
from typing import List, Dict, Any
import numpy as np


class VectorDBClient:
    """Base interface for vector database clients"""

    def embed_text(self, text: str) -> np.ndarray:
        """Convert text to embedding vector"""
        raise NotImplementedError

    def get_or_create_collection(self, name: str) -> 'Collection':
        """Get or create a named collection"""
        raise NotImplementedError


class Collection:
    """Base interface for vector collections"""

    def query(self, query_embeddings: np.ndarray, n_results: int) -> List[Dict[str, Any]]:
        """Search for similar vectors"""
        raise NotImplementedError

    def add(self, embeddings: List[np.ndarray], documents: List[str], metadatas: List[Dict]):
        """Add vectors to collection"""
        raise NotImplementedError


class MockVectorDBClient(VectorDBClient):
    """Simple in-memory implementation for testing"""

    def __init__(self):
        self.collections = {}

    def embed_text(self, text: str) -> np.ndarray:
        # Mock embedding - just return a random vector
        return np.random.rand(384)  # Common embedding size

    def get_or_create_collection(self, name: str) -> 'MockCollection':
        if name not in self.collections:
            self.collections[name] = MockCollection()
        return self.collections[name]


class MockCollection(Collection):
    def __init__(self):
        self.vectors = []
        self.documents = []
        self.metadatas = []

    def query(self, query_embeddings: np.ndarray, n_results: int) -> List[Dict[str, Any]]:
        # Mock query - return most recent entries
        n = min(n_results, len(self.documents))
        return [
            {"content": self.documents[i], "metadata": self.metadatas[i]}
            for i in range(-n, 0)
        ]

    def add(self, embeddings: List[np.ndarray], documents: List[str], metadatas: List[Dict]):
        self.vectors.extend(embeddings)
        self.documents.extend(documents)
        self.metadatas.extend(metadatas)
