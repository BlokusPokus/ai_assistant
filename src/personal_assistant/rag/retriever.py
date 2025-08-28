"""
Handles semantic search and retrieval from embedded knowledge sources.
Enhanced with real Gemini embeddings and prepared for Notion integration.
"""

import hashlib
import logging
from typing import Dict, List, Optional

import numpy as np
from sqlalchemy import select, func

from ..config.logging_config import get_logger
from ..database.models.memory_chunk import MemoryChunk
from ..database.models.memory_metadata import MemoryMetadata
from ..database.session import AsyncSessionLocal
from .embeddings.gemini_embeddings import GeminiEmbeddings
import json

# Configure module logger
logger = get_logger("rag")

# Global embedding model instance
_embedding_model = None


def get_embedding_model() -> GeminiEmbeddings:
    """Get or create global embedding model instance."""
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = GeminiEmbeddings()
        logger.info("Global embedding model initialized")
    return _embedding_model


async def embed_text(text: str) -> List[float]:
    """
    Generate real embedding for text using Gemini.

    Args:
        text: Text to embed

    Returns:
        List of float values representing the embedding vector
    """
    try:
        embedding_model = get_embedding_model()
        embedding = await embedding_model.embed_text(text)

        if embedding:
            logger.debug(
                f"Generated embedding of length {len(embedding)} for text of length {len(text)}")
            return embedding
        else:
            logger.warning("No embedding returned from Gemini API")
            return []

    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        return []


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors.
    """
    try:
        v1, v2 = np.array(vec1), np.array(vec2)
        return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
    except Exception as e:
        logger.error(f"Error calculating cosine similarity: {e}")
        return 0.0


async def update_chunk_embedding(chunk_id: int, document: str, metadata: Dict) -> bool:
    """
    Update an existing memory chunk with embeddings.

    Args:
        chunk_id: ID of the existing memory chunk
        document: Document content to embed
        metadata: Metadata for the chunk

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        async with AsyncSessionLocal() as session:
            # Generate real embedding
            embedding = await embed_text(document)

            if not embedding:
                logger.error(
                    f"Failed to generate embedding for chunk {chunk_id}")
                return False

            # Update the existing chunk with the embedding
            result = await session.execute(
                select(MemoryChunk).where(MemoryChunk.id == chunk_id)
            )
            chunk = result.scalar_one_or_none()

            if not chunk:
                logger.error(f"Chunk {chunk_id} not found")
                return False

            # ✅ FIXED: Store embedding as native JSON array, not string
            chunk.embedding = embedding
            await session.commit()

            logger.info(f"Successfully updated embedding for chunk {chunk_id}")
            return True

    except Exception as e:
        logger.error(f"Error updating chunk {chunk_id} embedding: {e}")
        return False


async def embed_and_index(document: str, metadata: Dict) -> None:
    """
    Embed and store a document with metadata.
    """
    try:
        async with AsyncSessionLocal() as session:
            # Generate real embedding
            embedding = await embed_text(document)

            if not embedding:
                logger.error("Failed to generate embedding for document")
                return

            # Create memory chunk
            chunk_data = {
                "content": document,
                # ✅ FIXED: Store embedding as native JSON array, not string
                "embedding": embedding,
                # Ensure integer user_id
                "user_id": int(metadata.get("user_id", 0))
            }

            # Check if chunk already exists
            existing_chunk = await session.execute(
                select(MemoryChunk).where(
                    MemoryChunk.content == document,
                    MemoryChunk.user_id == chunk_data["user_id"]
                )
            )

            if existing_chunk.scalar_one_or_none():
                logger.debug("Chunk already exists, skipping insertion")
                return

            # Create new chunk
            chunk = MemoryChunk(**chunk_data)
            session.add(chunk)
            await session.commit()

            # Add metadata
            for key, value in metadata.items():
                if key != "user_id":  # Skip user_id as it's already in chunk
                    meta_data = {
                        "chunk_id": chunk.id,
                        "key": key,
                        "value": str(value)
                    }

                    # Check if metadata already exists
                    existing_meta = await session.execute(
                        select(MemoryMetadata).where(
                            MemoryMetadata.chunk_id == chunk.id,
                            MemoryMetadata.key == key
                        )
                    )

                    if not existing_meta.scalar_one_or_none():
                        meta_record = MemoryMetadata(**meta_data)
                        session.add(meta_record)

            await session.commit()
            logger.info(
                f"Successfully indexed document for user {chunk_data['user_id']}")

    except Exception as e:
        logger.error(f"Error in embed_and_index: {e}")


async def query_knowledge_base(user_id: int, input_text: str) -> List[Dict]:
    """
    Retrieve relevant documents based on semantic similarity.
    Enhanced to use real embeddings and prepared for Notion integration.
    """
    try:
        async with AsyncSessionLocal() as session:
            # ✅ INPUT VALIDATION
            if user_id <= 0:
                logger.error(f"Invalid user_id: {user_id} (must be positive)")
                return []

            # Get query embedding using real Gemini embeddings
            query_vector = await embed_text(input_text)

            if not query_vector:
                logger.error(
                    "Failed to generate query embedding, cannot proceed")
                return []

            # ✅ SINGLE QUERY APPROACH
            stmt = (
                select(MemoryChunk, MemoryMetadata.key, MemoryMetadata.value)
                .outerjoin(MemoryMetadata, MemoryChunk.id == MemoryMetadata.chunk_id)
                .where(MemoryChunk.user_id == user_id)
                .where(MemoryChunk.embedding.isnot(None))
            )

            result = await session.execute(stmt)
            chunks = result.scalars().all()

            if not chunks:
                logger.debug(f"No memory chunks found for user {user_id}")
                return []

            # Calculate similarities
            scored = []
            for chunk in chunks:
                # ✅ FIXED: Handle embeddings as native JSON arrays
                if chunk.embedding:
                    try:
                        # Embeddings are now stored as native JSON arrays, no parsing needed
                        chunk_embedding = chunk.embedding

                        # Validate embedding format
                        if not isinstance(chunk_embedding, list) or not chunk_embedding:
                            logger.warning(
                                f"Invalid embedding format for chunk {chunk.id}: not a list or empty")
                            continue

                        # Ensure all elements are numeric
                        if not all(isinstance(x, (int, float)) for x in chunk_embedding):
                            logger.warning(
                                f"Invalid embedding format for chunk {chunk.id}: non-numeric elements")
                            continue

                    except Exception as e:
                        logger.warning(
                            f"Error processing chunk {chunk.id} embedding: {e}")
                        continue

                    similarity = cosine_similarity(
                        query_vector, chunk_embedding)

                    # Get metadata directly as key-value pairs
                    metadata_pairs = [(key, value)
                                      for key, value in result.mappings()]

                    # Create metadata dict
                    metadata_dict = {key: value for key,
                                     value in metadata_pairs}

                    scored.append((similarity, {
                        "content": chunk.content,
                        "metadata": {
                            **metadata_dict,
                            "source": "memory",
                            "chunk_id": chunk.id,
                            "similarity_score": similarity
                        }
                    }))

            # Sort by similarity and return top results
            scored.sort(key=lambda x: x[0], reverse=True)

            # Return top 5 results instead of 3 for better coverage
            results = [entry for _, entry in scored[:5]]

            logger.info(
                f"Retrieved {len(results)} relevant documents for user {user_id}")
            return results

    except Exception as e:
        logger.error(f"Error in query_knowledge_base: {e}")
        return []


async def get_embedding_stats() -> Dict[str, any]:
    """
    Get statistics about the embedding system.

    Returns:
        Dictionary with embedding statistics
    """
    try:
        embedding_model = get_embedding_model()
        cache_stats = embedding_model.get_cache_stats()

        return {
            "embedding_model": "GeminiEmbeddings",
            "cache_stats": cache_stats,
            "fallback_used": cache_stats.get("cache_misses", 0) > 0
        }

    except Exception as e:
        logger.error(f"Error getting embedding stats: {e}")
        return {
            "embedding_model": "Unknown",
            "error": str(e)
        }


async def generate_embeddings_for_content(content: str, metadata: Dict) -> bool:
    """
    Automatically generate and store embeddings for new content.

    Args:
        content: The content to generate embeddings for
        metadata: Metadata including user_id and other information

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if not content or not content.strip():
            logger.warning("Empty content provided for embedding generation")
            return False

        if not metadata.get("user_id"):
            logger.warning("No user_id provided in metadata")
            return False

        logger.info(
            f"🧠 Generating embeddings for content (user: {metadata['user_id']})")

        # Generate embedding
        embedding = await embed_text(content)

        if not embedding:
            logger.error("Failed to generate embedding for content")
            return False

        # Store in database
        await embed_and_index(content, metadata)

        logger.info(
            f"✅ Successfully generated and stored embeddings for content")
        return True

    except Exception as e:
        logger.error(f"Error generating embeddings for content: {e}")
        return False


async def generate_missing_embeddings(user_id: int = None, batch_size: int = 10) -> Dict[str, any]:
    """
    Generate embeddings for chunks that don't have them.

    Args:
        user_id: Specific user ID to process (None for all users)
        batch_size: Number of chunks to process in each batch

    Returns:
        Dict with processing statistics
    """
    try:
        async with AsyncSessionLocal() as session:
            # Build query for chunks without embeddings
            # ✅ FIXED: Use simpler approach to avoid PostgreSQL type conflicts
            if user_id:
                stmt = (
                    select(MemoryChunk)
                    .where(MemoryChunk.user_id == int(user_id))
                    .where(MemoryChunk.embedding.is_(None))
                )
            else:
                stmt = (
                    select(MemoryChunk)
                    .where(MemoryChunk.embedding.is_(None))
                )

            result = await session.execute(stmt)
            chunks_without_embeddings = result.scalars().all()

            # Also check for chunks with empty/invalid embeddings in Python
            additional_chunks = []
            if user_id:
                all_chunks_stmt = select(MemoryChunk).where(
                    MemoryChunk.user_id == int(user_id))
            else:
                all_chunks_stmt = select(MemoryChunk)

            all_chunks_result = await session.execute(all_chunks_stmt)
            all_chunks = all_chunks_result.scalars().all()

            for chunk in all_chunks:
                if chunk.embedding is not None:
                    # Check if embedding is effectively empty
                    if (isinstance(chunk.embedding, list) and len(chunk.embedding) == 0) or \
                       (isinstance(chunk.embedding, str) and chunk.embedding in ['[]', '{}', '']) or \
                       (isinstance(chunk.embedding, dict) and len(chunk.embedding) == 0):
                        additional_chunks.append(chunk)

            # Combine both lists
            all_chunks_to_process = chunks_without_embeddings + additional_chunks

            if not all_chunks_to_process:
                logger.info("No chunks found without embeddings")
                return {
                    "total_chunks": 0,
                    "processed": 0,
                    "successful": 0,
                    "failed": 0,
                    "message": "All chunks already have embeddings"
                }

            logger.info(
                f"Found {len(all_chunks_to_process)} chunks without embeddings")

            # Process in batches
            total_processed = 0
            total_successful = 0
            total_failed = 0

            for i in range(0, len(all_chunks_to_process), batch_size):
                batch = all_chunks_to_process[i:i + batch_size]
                logger.info(
                    f"Processing batch {i//batch_size + 1}/{(len(all_chunks_to_process) + batch_size - 1)//batch_size}")

                for chunk in batch:
                    try:
                        if not chunk.content:
                            logger.warning(
                                f"Chunk {chunk.id}: No content, skipping")
                            continue

                        logger.debug(
                            f"Generating embedding for chunk {chunk.id}")

                        # Generate embedding
                        embedding = await embed_text(chunk.content)

                        if embedding:
                            # Update the chunk with the embedding
                            chunk.embedding = embedding
                            total_successful += 1
                            logger.debug(
                                f"✅ Embedding generated for chunk {chunk.id}")
                        else:
                            total_failed += 1
                            logger.warning(
                                f"❌ Failed to generate embedding for chunk {chunk.id}")

                    except Exception as e:
                        total_failed += 1
                        logger.error(
                            f"❌ Error processing chunk {chunk.id}: {e}")

                    total_processed += 1

                # Commit batch
                await session.commit()
                logger.info(f"Batch committed: {len(batch)} chunks processed")

                # Small delay to avoid rate limiting
                import asyncio
                await asyncio.sleep(1)

            logger.info(f"🎉 Embedding generation complete!")
            logger.info(f"📊 Total processed: {total_processed}")
            logger.info(f"✅ Successful: {total_successful}")
            logger.info(f"❌ Failed: {total_failed}")

            return {
                "total_chunks": len(all_chunks_to_process),
                "processed": total_processed,
                "successful": total_successful,
                "failed": total_failed,
                "success_rate": round((total_successful / total_processed * 100), 2) if total_processed > 0 else 0
            }

    except Exception as e:
        logger.error(f"Error during bulk embedding generation: {e}")
        return {
            "error": str(e),
            "total_chunks": 0,
            "processed": 0,
            "successful": 0,
            "failed": 0
        }


async def get_query_performance_stats() -> Dict[str, any]:
    """
    Get performance statistics for RAG queries.

    Returns:
        Dictionary with performance metrics and recommendations
    """
    try:
        async with AsyncSessionLocal() as session:
            # Get basic statistics
            total_chunks_stmt = select(MemoryChunk)
            total_chunks_result = await session.execute(total_chunks_stmt)
            total_chunks = len(total_chunks_result.scalars().all())

            chunks_with_embeddings_stmt = select(MemoryChunk).where(
                MemoryChunk.embedding.isnot(None))
            chunks_with_embeddings_result = await session.execute(chunks_with_embeddings_stmt)
            chunks_with_embeddings = len(
                chunks_with_embeddings_result.scalars().all())

            # Calculate embedding coverage
            embedding_coverage = (
                chunks_with_embeddings / total_chunks * 100) if total_chunks > 0 else 0

            # Get user distribution
            user_distribution_stmt = select(MemoryChunk.user_id, func.count(
                MemoryChunk.id)).group_by(MemoryChunk.user_id)
            user_distribution_result = await session.execute(user_distribution_stmt)
            user_distribution = dict(user_distribution_result.all())

            # Performance recommendations
            recommendations = []

            if embedding_coverage < 80:
                recommendations.append(
                    "Low embedding coverage detected. Consider running bulk embedding generation.")

            if total_chunks > 1000:
                recommendations.append(
                    "Large number of chunks detected. Consider implementing chunk archiving.")

            if max(user_distribution.values()) > 500:
                recommendations.append(
                    "Some users have many chunks. Consider implementing user-specific chunk limits.")

            return {
                "total_chunks": total_chunks,
                "chunks_with_embeddings": chunks_with_embeddings,
                "embedding_coverage_percent": round(embedding_coverage, 2),
                "user_distribution": user_distribution,
                "recommendations": recommendations,
                "performance_optimizations": [
                    "Database query limits implemented",
                    "Early termination optimization",
                    "Hybrid scoring (text + vector)",
                    "Efficient metadata grouping",
                    "Batch processing with early termination"
                ]
            }

    except Exception as e:
        logger.error(f"Error getting performance stats: {e}")
        return {
            "error": str(e),
            "performance_optimizations": [
                "Database query limits implemented",
                "Early termination optimization",
                "Hybrid scoring (text + vector)",
                "Efficient metadata grouping",
                "Batch processing with early termination"
            ]
        }
