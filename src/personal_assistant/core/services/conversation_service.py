"""
ConversationService handles conversation management and state loading.
"""

from typing import Optional, Tuple
from personal_assistant.config.logging_config import get_logger
from personal_assistant.memory.conversation_manager import (
    create_new_conversation,
    get_conversation_id,
    should_resume_conversation,
)
from personal_assistant.memory.storage_integration import StorageIntegrationManager
from personal_assistant.types.state import AgentState

logger = get_logger("conversation_service")


class ConversationService:
    """Service for managing conversations and loading agent state."""
    
    def __init__(self, storage_manager: StorageIntegrationManager):
        """
        Initialize the conversation service.
        
        Args:
            storage_manager: Storage integration manager
        """
        self.storage_manager = storage_manager
    
    async def get_conversation_context(self, user_id: int, user_input: str) -> Tuple[str, AgentState]:
        """
        Get conversation context and agent state.
        
        Args:
            user_id: User identifier
            user_input: User's input message
            
        Returns:
            Tuple of (conversation_id, agent_state)
        """
        conversation_id = await get_conversation_id(user_id)
        
        if conversation_id is None:
            # Create new conversation
            conversation_id = await create_new_conversation(user_id)
            agent_state = AgentState(user_input=user_input)
            logger.info(f"Created new conversation: {conversation_id}")
            return conversation_id, agent_state
        
        # Check if we should resume existing conversation
        last_timestamp = await self.storage_manager.get_conversation_timestamp(
            user_id, conversation_id
        )
        
        resume_conversation = should_resume_conversation(last_timestamp)
        logger.info(f"Resume decision: {resume_conversation}")
        
        if resume_conversation:
            # Try to load existing state
            agent_state = await self.storage_manager.load_state(conversation_id, user_id)
            
            if agent_state is None:
                logger.warning("Failed to load existing conversation state, creating new conversation")
                conversation_id = await create_new_conversation(user_id)
                agent_state = AgentState(user_input=user_input)
            else:
                agent_state.user_input = user_input
                logger.info(f"Resumed conversation: {conversation_id}")
        else:
            # Create new conversation (previous one too old)
            conversation_id = await create_new_conversation(user_id)
            agent_state = AgentState(user_input=user_input)
            logger.info(f"Created new conversation (old one expired): {conversation_id}")
        
        # Reset state for new message
        agent_state.reset_for_new_message(user_input)
        
        return conversation_id, agent_state
