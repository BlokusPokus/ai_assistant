"""
Memory storage operations using the new database structure.
"""
from datetime import datetime, timezone
from typing import Optional, List, Dict
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from database.session import AsyncSessionLocal
from database.models.memory_chunk import MemoryChunk
from database.models.memory_metadata import MemoryMetadata
from database.crud.utils import add_record, filter_by, get_by_field
from sqlalchemy import desc


async def save_state(conversation_id: str, state: dict) -> None:
    """Save or update conversation state."""
    async with AsyncSessionLocal() as session:
        # Create memory chunk
        chunk_data = {
            "content": str(state),
            "embedding": None,  # JSON compatible null
            "created_at": datetime.utcnow()
        }
        chunk = await add_record(session, MemoryChunk, chunk_data)

        # Add metadata entries
        metadata_entries = [
            {"chunk_id": chunk.id, "key": "conversation_id", "value": conversation_id},
            {"chunk_id": chunk.id, "key": "type", "value": "state"},
            {"chunk_id": chunk.id, "key": "last_updated",
                "value": datetime.utcnow().isoformat()}
        ]

        for entry in metadata_entries:
            await add_record(session, MemoryMetadata, entry)


async def load_state(conversation_id: str) -> dict:
    """Load conversation state from database."""
    async with AsyncSessionLocal() as session:
        record = await get_by_field(
            session,
            MemoryChunk,
            field="meta_data->>'conversation_id'",
            value=conversation_id
        )
        return record.content if record else {}


async def get_conversation_timestamp(conversation_id: str) -> Optional[datetime]:
    """Get last update time for a conversation."""
    async with AsyncSessionLocal() as session:
        # Query for metadata with conversation_id
        stmt = (
            select(MemoryMetadata)
            .where(
                MemoryMetadata.key == "conversation_id",
                MemoryMetadata.value == conversation_id
            )
            .join(MemoryChunk)
            .options(joinedload(MemoryMetadata.chunk))
        )

        result = await session.execute(stmt)
        metadata = result.scalar_one_or_none()

        if metadata and metadata.chunk:
            # Find the last_updated metadata for this chunk
            for meta in metadata.chunk.meta_entries:
                if meta.key == "last_updated":
                    return datetime.fromisoformat(meta.value)
        return None


async def store_summary(user_id: str, summary: str) -> None:
    """Store conversation summary."""
    async with AsyncSessionLocal() as session:
        # Convert user_id string to int
        user_id_int = int(user_id)

        # Create memory chunk
        chunk_data = {
            "user_id": user_id_int,  # Now using integer
            "content": summary,
            "created_at": datetime.utcnow()
        }
        chunk = await add_record(session, MemoryChunk, chunk_data)

        # Add metadata
        metadata = {
            "chunk_id": chunk.id,
            "key": "type",
            "value": "summary"
        }
        await add_record(session, MemoryMetadata, metadata)


async def load_latest_summary(user_id: str) -> str:
    """Load most recent summary."""
    async with AsyncSessionLocal() as session:
        # Convert user_id string to int
        user_id_int = int(user_id)

        # Query for summary type metadata
        stmt = (
            select(MemoryChunk)
            .join(MemoryMetadata)
            .where(
                MemoryChunk.user_id == user_id_int,  # Now using integer
                MemoryMetadata.key == "type",
                MemoryMetadata.value == "summary"
            )
            .order_by(desc(MemoryChunk.created_at))
            .limit(1)
        )

        result = await session.execute(stmt)
        chunk = result.scalar_one_or_none()
        return chunk.content if chunk else ""


async def query_ltm(user_id: str, tags: List[str] = None) -> List[Dict]:
    """Query long-term memory with optional tags."""
    async with AsyncSessionLocal() as session:
        # Convert user_id string to int
        user_id_int = int(user_id)

        # Base query
        stmt = (
            select(MemoryChunk)
            .join(MemoryMetadata)
            .where(
                MemoryChunk.user_id == user_id_int,  # Now using integer
                MemoryMetadata.key == "type",
                MemoryMetadata.value == "ltm"
            )
        )

        # Add tag filtering if specified
        if tags:
            # Add additional joins for tag metadata
            stmt = stmt.join(MemoryMetadata,
                             MemoryMetadata.key == "tag",
                             MemoryMetadata.value.in_(tags))

        result = await session.execute(stmt)
        chunks = result.scalars().all()

        # Format results
        return [{"content": chunk.content, "metadata": {
            meta.key: meta.value for meta in chunk.meta_entries
        }} for chunk in chunks]


async def add_ltm_entry(user_id: str, entry: dict) -> None:
    """Add a structured long-term memory entry."""
    async with AsyncSessionLocal() as session:
        # Convert user_id string to int
        user_id_int = int(user_id)

        # Create the memory chunk
        chunk_data = {
            "user_id": user_id_int,  # Now using integer
            "content": entry.get("content"),
            "created_at": datetime.utcnow()
        }
        chunk = await add_record(session, MemoryChunk, chunk_data)

        # Add metadata entries
        metadata_entries = [
            {"chunk_id": chunk.id, "key": "type", "value": "ltm"},
            {"chunk_id": chunk.id, "key": "timestamp",
             "value": datetime.now(timezone.utc).isoformat()}
        ]

        # Add any additional metadata from entry
        for key, value in entry.items():
            if key != "content":
                metadata_entries.append({
                    "chunk_id": chunk.id,
                    "key": key,
                    "value": str(value)
                })

        for metadata in metadata_entries:
            await add_record(session, MemoryMetadata, metadata)


# def save_conversation_state(conversation_id: str, state: dict) -> None:
#     """Save the conversation state in memory."""
#     # Implementation for in-memory storage
#     pass


# def load_conversation_state(conversation_id: str) -> dict:
#     """Load the conversation state from memory."""
#     # Implementation for in-memory retrieval
#     pass
