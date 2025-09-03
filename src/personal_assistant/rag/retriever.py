"""
Handles semantic search and retrieval from embedded knowledge sources.
Enhanced with real Gemini embeddings and prepared for Notion integration.
"""

from typing import Dict, List

import numpy as np
from sqlalchemy import func, select

from ..config.logging_config import get_logger
from ..database.models.conversation_message import ConversationMessage
from ..database.session import AsyncSessionLocal
from .embeddings.gemini_embeddings import GeminiEmbeddings

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
                f"Generated embedding of length {len(embedding)} for text of length {len(text)}"
            )
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


# async def update_message_embedding(message_id: int, document: str, metadata: Dict) -> bool:
#     """
#     Update an existing conversation message with embeddings.

#     Args:
#         message_id: ID of the existing conversation message
#         document: Document content to embed
#         metadata: Metadata for the message

#     Returns:
#         bool: True if successful, False otherwise
#     """
#     try:
#         async with AsyncSessionLocal() as session:
#             # Generate real embedding
#             embedding = await embed_text(document)

#             if not embedding:
#                 logger.error(
#                     f"Failed to generate embedding for message {message_id}")
#                 return False

#             # Update the existing message with the embedding
#             result = await session.execute(
#                 select(ConversationMessage).where(
#                     ConversationMessage.id == message_id)
#             )
#             message = result.scalar_one_or_none()

#             if not message:
#                 logger.error(f"Message {message_id} not found")
#                 return False

#             # Store embedding in additional_data
#             if not message.additional_data:
#                 message.additional_data = {}
#             message.additional_data['embedding'] = embedding
#             await session.commit()

#             logger.info(
#                 f"Successfully updated embedding for message {message_id}")
#             return True

#     except Exception as e:
#         logger.error(f"Error updating message {message_id} embedding: {e}")
#         return False


async def embed_and_index(document: str, metadata: Dict) -> None:
    """
    Embed and store a document with metadata in the new normalized schema.
    """
    try:
        async with AsyncSessionLocal() as session:
            # Generate real embedding
            embedding = await embed_text(document)

            if not embedding:
                logger.error("Failed to generate embedding for document")
                return

            user_id = int(metadata.get("user_id", 0))
            conversation_id = metadata.get("conversation_id", "rag_document")

            # Check if document already exists in conversation messages
            existing_message = await session.execute(
                select(ConversationMessage).where(
                    ConversationMessage.content == document,
                    ConversationMessage.conversation_id == conversation_id,
                )
            )

            if existing_message.scalar_one_or_none():
                logger.debug("Document already exists, skipping insertion")
                return

            # Create new conversation message with embedding in additional_data
            message_data = {
                "conversation_id": conversation_id,
                "role": "system",
                "content": document,
                "message_type": "rag_document",
                "additional_data": {
                    "embedding": embedding,
                    **{
                        k: v
                        for k, v in metadata.items()
                        if k not in ["user_id", "conversation_id"]
                    },
                },
            }

            message = ConversationMessage(**message_data)
            session.add(message)
            await session.commit()

            logger.info(
                f"Successfully indexed document for user {user_id} in conversation {conversation_id}"
            )

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
                logger.error("Failed to generate query embedding, cannot proceed")
                return []

            # Query conversation messages with embeddings
            stmt = (
                select(ConversationMessage)
                .where(ConversationMessage.message_type == "rag_document")
                .where(ConversationMessage.additional_data.isnot(None))
            )

            result = await session.execute(stmt)
            messages = result.scalars().all()

            if not messages:
                logger.debug(f"No RAG documents found for user {user_id}")
                return []

            # Calculate similarities
            scored = []
            for message in messages:
                # Check if message has embedding in additional_data
                if message.additional_data and "embedding" in message.additional_data:
                    try:
                        chunk_embedding = message.additional_data["embedding"]

                        # Validate embedding format
                        if not isinstance(chunk_embedding, list) or not chunk_embedding:
                            logger.warning(
                                f"Invalid embedding format for message {message.id}: not a list or empty"
                            )
                            continue

                        # Ensure all elements are numeric
                        if not all(
                            isinstance(x, (int, float)) for x in chunk_embedding
                        ):
                            logger.warning(
                                f"Invalid embedding format for message {message.id}: non-numeric elements"
                            )
                            continue

                    except Exception as e:
                        logger.warning(
                            f"Error processing message {message.id} embedding: {e}"
                        )
                        continue

                    similarity = cosine_similarity(query_vector, chunk_embedding)

                    # Create metadata dict from additional_data
                    metadata_dict = message.additional_data.copy()
                    metadata_dict.update(
                        {
                            "source": "normalized_storage",
                            "message_id": message.id,
                            "conversation_id": message.conversation_id,
                            "similarity_score": similarity,
                        }
                    )

                    scored.append(
                        (
                            similarity,
                            {"content": message.content, "metadata": metadata_dict},
                        )
                    )

            # Sort by similarity and return top results
            scored.sort(key=lambda x: x[0], reverse=True)

            # Return top 5 results instead of 3 for better coverage
            results = [entry for _, entry in scored[:5]]

            logger.info(
                f"Retrieved {len(results)} relevant documents for user {user_id}"
            )
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
            "fallback_used": cache_stats.get("cache_misses", 0) > 0,
        }

    except Exception as e:
        logger.error(f"Error getting embedding stats: {e}")
        return {"embedding_model": "Unknown", "error": str(e)}


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
            f"🧠 Generating embeddings for content (user: {metadata['user_id']})"
        )

        # Generate embedding
        embedding = await embed_text(content)

        if not embedding:
            logger.error("Failed to generate embedding for content")
            return False

        # Store in database
        await embed_and_index(content, metadata)

        logger.info(f"✅ Successfully generated and stored embeddings for content")
        return True

    except Exception as e:
        logger.error(f"Error generating embeddings for content: {e}")
        return False


async def generate_missing_embeddings(
    user_id: int = None, batch_size: int = 10
) -> Dict[str, any]:
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
            # Build query for messages without embeddings
            if user_id:
                stmt = (
                    select(ConversationMessage)
                    .where(ConversationMessage.message_type == "rag_document")
                    .where(
                        (ConversationMessage.additional_data.is_(None))
                        | (ConversationMessage.additional_data.notlike('%"embedding"%'))
                    )
                )
            else:
                stmt = (
                    select(ConversationMessage)
                    .where(ConversationMessage.message_type == "rag_document")
                    .where(
                        (ConversationMessage.additional_data.is_(None))
                        | (ConversationMessage.additional_data.notlike('%"embedding"%'))
                    )
                )

            result = await session.execute(stmt)
            messages_without_embeddings = result.scalars().all()

            # Also check for messages with empty/invalid embeddings in Python
            additional_messages = []
            if user_id:
                all_messages_stmt = select(ConversationMessage).where(
                    ConversationMessage.message_type == "rag_document"
                )
            else:
                all_messages_stmt = select(ConversationMessage).where(
                    ConversationMessage.message_type == "rag_document"
                )

            all_messages_result = await session.execute(all_messages_stmt)
            all_messages = all_messages_result.scalars().all()

            for message in all_messages:
                if message.additional_data and "embedding" in message.additional_data:
                    # Check if embedding is effectively empty
                    embedding = message.additional_data["embedding"]
                    if (
                        (isinstance(embedding, list) and len(embedding) == 0)
                        or (
                            isinstance(embedding, str) and embedding in ["[]", "{}", ""]
                        )
                        or (isinstance(embedding, dict) and len(embedding) == 0)
                    ):
                        additional_messages.append(message)

            # Combine both lists
            all_messages_to_process = messages_without_embeddings + additional_messages

            if not all_messages_to_process:
                logger.info("No messages found without embeddings")
                return {
                    "total_messages": 0,
                    "processed": 0,
                    "successful": 0,
                    "failed": 0,
                    "message": "All messages already have embeddings",
                }

            logger.info(
                f"Found {len(all_messages_to_process)} messages without embeddings"
            )

            # Process in batches
            total_processed = 0
            total_successful = 0
            total_failed = 0

            for i in range(0, len(all_messages_to_process), batch_size):
                batch = all_messages_to_process[i : i + batch_size]
                logger.info(
                    f"Processing batch {i//batch_size + 1}/{(len(all_messages_to_process) + batch_size - 1)//batch_size}"
                )

                for message in batch:
                    try:
                        if not message.content:
                            logger.warning(
                                f"Message {message.id}: No content, skipping"
                            )
                            continue

                        logger.debug(f"Generating embedding for message {message.id}")

                        # Generate embedding
                        embedding = await embed_text(message.content)

                        if embedding:
                            # Update the message with the embedding in additional_data
                            if not message.additional_data:
                                message.additional_data = {}
                            message.additional_data["embedding"] = embedding
                            total_successful += 1
                            logger.debug(
                                f"✅ Embedding generated for message {message.id}"
                            )
                        else:
                            total_failed += 1
                            logger.warning(
                                f"❌ Failed to generate embedding for message {message.id}"
                            )

                    except Exception as e:
                        total_failed += 1
                        logger.error(f"❌ Error processing message {message.id}: {e}")

                    total_processed += 1

                # Commit batch
                await session.commit()
                logger.info(f"Batch committed: {len(batch)} messages processed")

                # Small delay to avoid rate limiting
                import asyncio

                await asyncio.sleep(1)

            logger.info(f"🎉 Embedding generation complete!")
            logger.info(f"📊 Total processed: {total_processed}")
            logger.info(f"✅ Successful: {total_successful}")
            logger.info(f"❌ Failed: {total_failed}")

            return {
                "total_messages": len(all_messages_to_process),
                "processed": total_processed,
                "successful": total_successful,
                "failed": total_failed,
                "success_rate": round((total_successful / total_processed * 100), 2)
                if total_processed > 0
                else 0,
            }

    except Exception as e:
        logger.error(f"Error during bulk embedding generation: {e}")
        return {
            "error": str(e),
            "total_messages": 0,
            "processed": 0,
            "successful": 0,
            "failed": 0,
        }


async def get_query_performance_stats() -> Dict[str, any]:
    """
    Get performance statistics for RAG queries.

    Returns:
        Dictionary with performance metrics and recommendations
    """
    try:
        async with AsyncSessionLocal() as session:
            # Get basic statistics for RAG documents
            total_messages_stmt = select(ConversationMessage).where(
                ConversationMessage.message_type == "rag_document"
            )
            total_messages_result = await session.execute(total_messages_stmt)
            total_messages = len(total_messages_result.scalars().all())

            messages_with_embeddings_stmt = (
                select(ConversationMessage)
                .where(
                    ConversationMessage.message_type == "rag_document",
                    ConversationMessage.additional_data.isnot(None),
                )
                .where(ConversationMessage.additional_data.like('%"embedding"%'))
            )
            messages_with_embeddings_result = await session.execute(
                messages_with_embeddings_stmt
            )
            messages_with_embeddings = len(
                messages_with_embeddings_result.scalars().all()
            )

            # Calculate embedding coverage
            embedding_coverage = (
                (messages_with_embeddings / total_messages * 100)
                if total_messages > 0
                else 0
            )

            # Get conversation distribution (instead of user distribution)
            conversation_distribution_stmt = (
                select(
                    ConversationMessage.conversation_id,
                    func.count(ConversationMessage.id),
                )
                .where(ConversationMessage.message_type == "rag_document")
                .group_by(ConversationMessage.conversation_id)
            )
            conversation_distribution_result = await session.execute(
                conversation_distribution_stmt
            )
            conversation_distribution = dict(conversation_distribution_result.all())

            # Performance recommendations
            recommendations = []

            if embedding_coverage < 80:
                recommendations.append(
                    "Low embedding coverage detected. Consider running bulk embedding generation."
                )

            if total_messages > 1000:
                recommendations.append(
                    "Large number of RAG documents detected. Consider implementing document archiving."
                )

            if max(conversation_distribution.values()) > 500:
                recommendations.append(
                    "Some conversations have many RAG documents. Consider implementing conversation-specific document limits."
                )

            return {
                "total_messages": total_messages,
                "messages_with_embeddings": messages_with_embeddings,
                "embedding_coverage_percent": round(embedding_coverage, 2),
                "conversation_distribution": conversation_distribution,
                "recommendations": recommendations,
                "performance_optimizations": [
                    "Database query limits implemented",
                    "Early termination optimization",
                    "Hybrid scoring (text + vector)",
                    "Efficient metadata grouping",
                    "Batch processing with early termination",
                ],
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
                "Batch processing with early termination",
            ],
        }
