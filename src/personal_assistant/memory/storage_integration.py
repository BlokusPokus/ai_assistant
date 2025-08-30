"""
Storage Integration Layer for Task 053: Database Schema Redesign

This module provides a clean interface to the new normalized storage system,
enabling efficient state management with structured, queryable data.
"""

import logging
import time
from typing import Optional, Union
from datetime import datetime, timezone

from ..config.logging_config import get_logger
from ..config.feature_flags import use_normalized_storage, normalized_storage_logging
from ..types.state import AgentState
from .normalized_storage import (
    save_state_normalized,
    load_state_normalized,
    update_state_partial,
    delete_conversation_normalized
)
from ..database.session import AsyncSessionLocal

logger = get_logger("storage_integration")


class StorageIntegrationManager:
    """
    Manages the new normalized storage system.

    This class provides a clean interface to the normalized storage operations,
    with intelligent context loading and efficient state management.
    """

    def __init__(self):
        self.use_normalized = use_normalized_storage()
        self.logging_enabled = normalized_storage_logging()

        if not self.use_normalized:
            logger.warning(
                "⚠️ Normalized storage is disabled. Enable with USE_NORMALIZED_STORAGE=true")

        logger.info(f"🔧 Storage Integration Manager initialized:")
        logger.info(f"  Use normalized storage: {self.use_normalized}")
        logger.info(f"  Detailed logging: {self.logging_enabled}")

    async def save_state(
        self,
        conversation_id: str,
        state: AgentState,
        user_id: int
    ) -> bool:
        """
        Save conversation state using the new normalized database schema.

        Args:
            conversation_id: Unique identifier for the conversation
            state: The conversation state to save
            user_id: User ID for the conversation (required)

        Returns:
            True if save successful, False otherwise

        Raises:
            ValueError: If user_id is not provided
        """
        if not user_id:
            raise ValueError("user_id is required for normalized storage")

        if not self.use_normalized:
            raise RuntimeError(
                "Normalized storage is disabled. Enable with USE_NORMALIZED_STORAGE=true")

        logger.info(f"💾 Saving state for conversation: {conversation_id}")

        try:
            await save_state_normalized(conversation_id, state, user_id)
            logger.info(
                f"✅ Successfully saved state for conversation {conversation_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to save state for {conversation_id}: {e}")
            return False

    async def load_state(
        self,
        conversation_id: str,
        user_id: int,
        max_messages: int = 50,
        max_context_items: int = 20,
        min_relevance_score: float = 0.3
    ) -> Optional[AgentState]:
        """
        Load conversation state using the new normalized database schema.

        This function provides intelligent, selective loading:
        1. Loads core conversation state efficiently
        2. Loads only relevant messages based on limits
        3. Loads high-quality context items based on relevance scores
        4. Reconstructs AgentState object with loaded data

        Args:
            conversation_id: Unique identifier for the conversation
            user_id: User ID for the conversation (required)
            max_messages: Maximum number of messages to load
            max_context_items: Maximum number of context items to load
            min_relevance_score: Minimum relevance score for context items

        Returns:
            AgentState object if found, None otherwise

        Raises:
            ValueError: If user_id is not provided
        """
        if not user_id:
            raise ValueError("user_id is required for normalized storage")

        if not self.use_normalized:
            raise RuntimeError(
                "Normalized storage is disabled. Enable with USE_NORMALIZED_STORAGE=true")

        logger.info(f"📂 Loading state for conversation: {conversation_id}")

        try:
            state = await load_state_normalized(
                conversation_id,
                user_id,
                max_messages=max_messages,
                max_context_items=max_context_items,
                min_relevance_score=min_relevance_score
            )

            if state:
                logger.info(
                    f"✅ Successfully loaded state for conversation {conversation_id}")
                logger.info(
                    f"  Messages loaded: {len(state.conversation_history)}")
                logger.info(
                    f"  Context items loaded: {len(state.memory_context)}")
            else:
                logger.warning(
                    f"⚠️ No state found for conversation {conversation_id}")

            return state

        except Exception as e:
            logger.error(f"❌ Failed to load state for {conversation_id}: {e}")
            return None

    async def update_state_partial(
        self,
        conversation_id: str,
        updates: dict,
        user_id: int
    ) -> bool:
        """
        Update specific parts of a conversation state using normalized schema.

        This function enables efficient partial updates without loading/saving entire state:
        1. Updates only specified fields in conversation_states
        2. Adds new messages without replacing all messages
        3. Updates context items incrementally
        4. Maintains data consistency and referential integrity

        Args:
            conversation_id: Unique identifier for the conversation
            updates: Dictionary of fields to update
            user_id: User ID for validation

        Returns:
            True if update successful, False otherwise
        """
        if not user_id:
            raise ValueError("user_id is required for normalized storage")

        if not self.use_normalized:
            raise RuntimeError(
                "Normalized storage is disabled. Enable with USE_NORMALIZED_STORAGE=true")

        logger.info(
            f"🔄 Updating state partially for conversation: {conversation_id}")

        try:
            success = await update_state_partial(
                conversation_id, updates, user_id)
            if success:
                logger.info(
                    f"✅ Successfully updated state for conversation {conversation_id}")
            else:
                logger.warning(
                    f"⚠️ Partial update failed for conversation {conversation_id}")
            return success

        except Exception as e:
            logger.error(
                f"❌ Failed to update state for {conversation_id}: {e}")
            return False

    async def delete_conversation(
        self,
        conversation_id: str,
        user_id: int
    ) -> bool:
        """
        Delete a conversation and all associated data using normalized schema.

        This function provides complete cleanup:
        1. Deletes conversation state
        2. Deletes all associated messages
        3. Deletes all associated context items
        4. Deletes all associated metadata
        5. Maintains referential integrity with CASCADE deletes

        Args:
            conversation_id: Unique identifier for the conversation
            user_id: User ID for validation

        Returns:
            True if deletion successful, False otherwise
        """
        if not user_id:
            raise ValueError("user_id is required for normalized storage")

        if not self.use_normalized:
            raise RuntimeError(
                "Normalized storage is disabled. Enable with USE_NORMALIZED_STORAGE=true")

        logger.info(
            f"🗑️ Deleting conversation: {conversation_id}")

        try:
            success = await delete_conversation_normalized(
                conversation_id, user_id)
            if success:
                logger.info(
                    f"✅ Successfully deleted conversation {conversation_id}")
            else:
                logger.warning(
                    f"⚠️ Deletion failed for conversation {conversation_id}")
            return success

        except Exception as e:
            logger.error(
                f"❌ Failed to delete conversation {conversation_id}: {e}")
            return False

    async def get_conversation_timestamp(
        self,
        user_id: int,
        conversation_id: str
    ) -> Optional[datetime]:
        """
        Get last update time for a conversation using the new normalized database schema.

        Args:
            user_id: User ID for the conversation
            conversation_id: Conversation identifier

        Returns:
            Last update timestamp if found, None otherwise
        """
        if not self.use_normalized:
            raise RuntimeError(
                "Normalized storage is disabled. Enable with USE_NORMALIZED_STORAGE=true")

        try:
            from sqlalchemy import select
            from ..database.models.conversation_state import ConversationState

            async with AsyncSessionLocal() as session:
                stmt = select(ConversationState.updated_at).where(
                    ConversationState.conversation_id == conversation_id,
                    ConversationState.user_id == user_id
                )
                result = await session.execute(stmt)
                timestamp = result.scalar_one_or_none()

                if timestamp:
                    logger.debug(
                        f"Found timestamp in normalized storage: {conversation_id}")
                    return timestamp
                else:
                    logger.debug(
                        f"No timestamp found in normalized storage: {conversation_id}")
                    return None

        except Exception as e:
            logger.error(
                f"❌ Failed to get timestamp for {conversation_id}: {e}")
            return None

    async def log_agent_interaction(
        self,
        user_id: int,
        user_input: str,
        agent_response: str,
        tool_called: str = None,
        tool_output: str = None,
        memory_used: list = None,
        timestamp: datetime = None
    ) -> bool:
        """
        Log agent interaction using the new normalized database schema.

        Args:
            user_id: User ID for the interaction
            user_input: User's input message
            agent_response: Agent's response
            tool_called: Name of tool used (optional)
            tool_output: Output from tool (optional)
            memory_used: Memory context used (optional)
            timestamp: When interaction occurred (optional)

        Returns:
            True if logging successful, False otherwise
        """
        if not self.use_normalized:
            raise RuntimeError(
                "Normalized storage is disabled. Enable with USE_NORMALIZED_STORAGE=true")

        try:
            # For now, we'll skip interaction logging since it requires a valid conversation_id
            # This avoids the foreign key constraint issue
            # TODO: Implement proper interaction logging in the new schema
            logger.debug(
                f"Interaction logging skipped for user {user_id} (not yet implemented in new schema)")
            return True

        except Exception as e:
            logger.error(
                f"❌ Failed to log interaction for user {user_id}: {e}")
            return False

    def get_storage_info(self) -> dict:
        """
        Get information about the current storage configuration.

        Returns:
            Dictionary with storage configuration information
        """
        return {
            'use_normalized_storage': self.use_normalized,
            'current_storage_system': 'normalized' if self.use_normalized else 'disabled',
            'supports_partial_updates': self.use_normalized,
            'supports_intelligent_loading': self.use_normalized,
            'detailed_logging': self.logging_enabled
        }

    def validate_configuration(self) -> bool:
        """
        Validate that the storage system is properly configured.

        Returns:
            True if configuration is valid, False otherwise
        """
        if not self.use_normalized:
            logger.error("❌ Normalized storage is disabled")
            return False

        logger.info("✅ Storage configuration is valid")
        return True


# Global storage integration manager instance
_storage_integration_manager = None


def get_storage_integration_manager() -> StorageIntegrationManager:
    """Get or create the global storage integration manager instance."""
    global _storage_integration_manager
    if _storage_integration_manager is None:
        _storage_integration_manager = StorageIntegrationManager()
    return _storage_integration_manager


# Convenience functions for easy access
async def save_state_integrated(
    conversation_id: str,
    state: AgentState,
    user_id: int
) -> bool:
    """Save state using the integrated storage system."""
    manager = get_storage_integration_manager()
    return await manager.save_state(conversation_id, state, user_id)


async def load_state_integrated(
    conversation_id: str,
    user_id: int,
    max_messages: int = 50,
    max_context_items: int = 20,
    min_relevance_score: float = 0.3
) -> Optional[AgentState]:
    """Load state using the integrated storage system."""
    manager = get_storage_integration_manager()
    return await manager.load_state(
        conversation_id,
        user_id,
        max_messages=max_messages,
        max_context_items=max_context_items,
        min_relevance_score=min_relevance_score
    )


async def update_state_partial_integrated(
    conversation_id: str,
    updates: dict,
    user_id: int
) -> bool:
    """Update state partially using the integrated storage system."""
    manager = get_storage_integration_manager()
    return await manager.update_state_partial(conversation_id, updates, user_id)


async def delete_conversation_integrated(
    conversation_id: str,
    user_id: int
) -> bool:
    """Delete conversation using the integrated storage system."""
    manager = get_storage_integration_manager()
    return await manager.delete_conversation(conversation_id, user_id)


def get_storage_info() -> dict:
    """Get information about the current storage configuration."""
    manager = get_storage_integration_manager()
    return manager.get_storage_info()


def validate_storage_configuration() -> bool:
    """Validate that the storage system is properly configured."""
    manager = get_storage_integration_manager()
    return manager.validate_configuration()
