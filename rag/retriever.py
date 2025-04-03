
"""
Handles semantic search and retrieval from embedded knowledge sources.
"""

from typing import List, Dict
import hashlib
import numpy as np

# Simulated in-memory vector store
vector_store = []


def fake_embed(text: str) -> List[float]:
    """
    A fake embedding generator (replace with real LLM-based embeddings).
    """
    np.random.seed(
        int(hashlib.sha256(text.encode()).hexdigest(), 16) % (2**32))
    return np.random.rand(512).tolist()


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors.
    """
    v1, v2 = np.array(vec1), np.array(vec2)
    return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))


def embed_and_index(document: str, metadata: Dict) -> None:
    """
    Embed and store a document in the vector store with metadata.
    """
    embedding = fake_embed(document)
    vector_store.append({
        "embedding": embedding,
        "document": document,
        "metadata": metadata
    })


def query_knowledge_base(user_id: str, input_text: str) -> List[Dict]:
    """
    Retrieve relevant documents from the vector store based on semantic similarity.
    """
    query_vector = fake_embed(input_text)
    scored = []

    for entry in vector_store:
        if entry["metadata"].get("user_id") == user_id:
            similarity = cosine_similarity(query_vector, entry["embedding"])
            scored.append((similarity, entry))

    # Return top 3 matches
    scored.sort(key=lambda x: x[0], reverse=True)
    return [entry for _, entry in scored[:3]]
