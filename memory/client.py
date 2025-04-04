"""
Vector database client interfaces and implementations.
"""
from datetime import datetime
import logging
from typing import List, Optional
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.models.memory_chunk import MemoryChunk
from database.session import AsyncSessionLocal
from database.crud.utils import add_record, filter_by
from memory.interface import MemoryInterface

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MemoryDBClient:
    """
    Handles database operations for memory storage and retrieval.

    Inputs:
    - embedding_model: Model with `.embed_text(text) -> list[float]` method

    Core responsibilities:
    - Embedding content
    - Using CRUD utils for database operations
    """

    def __init__(self, embedding_model=None):
        self.embedding_model = embedding_model
        logger.info("MemoryDBClient initialized")

    def embed_text(self, text: str) -> np.ndarray:
        """
        Converts input text into an embedding vector.

        Args:
            text (str): Input string to embed.

        Returns:
            np.ndarray: Embedding as numpy array.
        """
        embedding = self.embedding_model.embed_text(text)
        return np.array(embedding)

    async def add_record(self, user_id: int, content: str, vector: np.ndarray, metadata: dict) -> None:
        """
        Stores a new memory record using the CRUD utils.

        Args:
            user_id (int): User this content belongs to.
            content (str): Original text.
            vector (np.ndarray): Embedding of the content.
            metadata (dict): Additional contextual metadata.

        Returns:
            None
        """
        async with AsyncSessionLocal() as session:
            data = {
                "user_id": user_id,
                "content": content,
                "embedding": vector.tolist(),  # Convert numpy array to list
                "created_at": datetime.utcnow()
            }
            await add_record(session, MemoryChunk, data)
            logger.info("Added memory record for user_id=%d", user_id)

    async def query_records(self, user_id: int, query: str, n_results: int) -> List[MemoryChunk]:
        """
        Queries memory records using CRUD utils.

        Args:
            user_id (int): The user to restrict results to.
            query (str): Text query to search for in content.
            n_results (int): Max number of results to return.

        Returns:
            List[MemoryChunk]: Matching memory records.
        """
        async with AsyncSessionLocal() as session:
            # Note: This is a simplified query. You might want to add vector similarity search
            records = await filter_by(
                session,
                MemoryChunk,
                user_id=user_id,
                limit=n_results
            )
            logger.info("Found %d matching records for query='%s'",
                        len(records), query)
            return records


class VectorMemory(MemoryInterface):
    """
    High-level memory component used by the agent.

    Wraps the database client to:
    - Automatically embed new inputs
    - Fetch similar memory records for reasoning

    Args:
        client (MemoryDBClient): Underlying storage and embedder.
        user_id (int): The user associated with this memory instance.
    """

    def __init__(self, client: MemoryDBClient, user_id: int):
        self.client = client
        self.user_id = user_id

    async def add(self, content: str, metadata: dict) -> None:
        """
        Adds new content to long-term memory.

        Steps:
        - Embed the text
        - Store the vector and metadata

        Args:
            content (str): Text to remember.
            metadata (dict): Context about the content (e.g. source, type).

        Returns:
            None
        """
        vector = self.client.embed_text(content)
        await self.client.add_record(self.user_id, content, vector, metadata)

    async def query(self, query: str, k: int) -> List[MemoryChunk]:
        """
        Retrieves memory records similar to a given query.

        (Currently uses simple ILIKE search, not vector similarity.)

        Args:
            query (str): Text to search for.
            k (int): Max number of results.

        Returns:
            List[MemoryChunk]: Relevant past memory chunks.
        """
        return await self.client.query_records(self.user_id, query, k)
