"""
Handles semantic search and retrieval from embedded knowledge sources.
"""

from typing import List, Dict
import hashlib
import numpy as np
from sqlalchemy import select
from database.session import AsyncSessionLocal
from database.models.memory_chunk import MemoryChunk
from database.models.memory_metadata import MemoryMetadata

# Simulated in-memory vector store
vector_store = []


async def fake_embed(text: str) -> List[float]:
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


async def embed_and_index(document: str, metadata: Dict) -> None:
    """
    Embed and store a document with metadata.
    """
    async with AsyncSessionLocal() as session:
        # Generate embedding
        embedding = await fake_embed(document)

        # Create memory chunk
        chunk_data = {
            "content": document,
            "embedding": str(embedding),  # Convert embedding to string
            # Ensure integer user_id
            "user_id": int(metadata.get("user_id", 0))
        }
        chunk = await session.execute(
            select(MemoryChunk).where(
                MemoryChunk.content == document,
                MemoryChunk.user_id == chunk_data["user_id"]
            )
        )

        # Add metadata
        for key, value in metadata.items():
            meta_data = {
                "chunk_id": chunk.id,
                "key": key,
                "value": str(value)
            }
            await session.execute(
                select(MemoryMetadata).where(
                    MemoryMetadata.chunk_id == chunk.id,
                    MemoryMetadata.key == key
                )
            )


async def query_knowledge_base(user_id: str, input_text: str) -> List[Dict]:
    """
    Retrieve relevant documents based on semantic similarity.
    """
    async with AsyncSessionLocal() as session:
        # Convert user_id to integer
        user_id_int = int(user_id)

        # Get query embedding
        query_vector = await fake_embed(input_text)

        # Get all documents for user
        stmt = (
            select(MemoryChunk)
            .where(MemoryChunk.user_id == user_id_int)
            .join(MemoryMetadata)
        )

        result = await session.execute(stmt)
        chunks = result.scalars().all()

        # Calculate similarities
        scored = []
        for chunk in chunks:
            if chunk.embedding:  # Check if embedding exists
                # Convert string back to list
                chunk_embedding = eval(chunk.embedding)
                similarity = cosine_similarity(query_vector, chunk_embedding)
                scored.append((similarity, {
                    "content": chunk.content,
                    "metadata": {
                        meta.key: meta.value for meta in chunk.meta_entries
                    }
                }))

        # Sort by similarity and return top 3
        scored.sort(key=lambda x: x[0], reverse=True)
        return [entry for _, entry in scored[:3]]
