"""
Chat Service for Task 073: Chat Integration with Agent Service.

This service handles chat conversation management, message processing,
and integration with the AgentCore service.
"""

import logging
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from personal_assistant.core import AgentCore
from personal_assistant.database.models.conversation_state import ConversationState
from personal_assistant.database.models.conversation_message import ConversationMessage

logger = logging.getLogger(__name__)


class ChatService:
    """Service for managing chat conversations and messages."""

    def __init__(self, agent_core: AgentCore):
        self.agent_core = agent_core


    async def get_user_conversations(
        self,
        db: AsyncSession,
        user_id: int,
        page: int = 1,
        per_page: int = 20
    ) -> Tuple[List[ConversationState], int]:
        """Get user's conversations with pagination."""
        # Get total count
        count_query = select(func.count(ConversationState.id)).where(ConversationState.user_id == user_id)
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Get conversations
        offset = (page - 1) * per_page
        query = (
            select(ConversationState)
            .where(ConversationState.user_id == user_id)
            .order_by(ConversationState.updated_at.desc())
            .offset(offset)
            .limit(per_page)
        )
        result = await db.execute(query)
        conversations = result.scalars().all()

        logger.info(f"Retrieved {len(conversations)} conversations for user {user_id}")
        
        # Debug: Log conversation details
        for i, conv in enumerate(conversations):
            logger.info(f"Conversation {i}: ID={conv.id}, conversation_id={conv.conversation_id}, user_id={conv.user_id}, step_count={conv.step_count}, created_at={conv.created_at}")
        
        return conversations, total

    async def get_conversation_messages(
        self,
        db: AsyncSession,
        conversation_id: str,
        user_id: int,
        limit: int = 50
    ) -> List[ConversationMessage]:
        """Get messages for a conversation."""
        # First verify the conversation belongs to the user
        conv_query = select(ConversationState).where(
            ConversationState.conversation_id == conversation_id,
            ConversationState.user_id == user_id
        )
        conv_result = await db.execute(conv_query)
        conversation = conv_result.scalar_one_or_none()
        
        if not conversation:
            raise ValueError("Conversation not found or access denied")

        query = (
            select(ConversationMessage)
            .where(ConversationMessage.conversation_id == conversation_id)
            .order_by(ConversationMessage.id.asc())
            .limit(limit)
        )
        result = await db.execute(query)
        messages = result.scalars().all()
        
        logger.info(f"Retrieved {len(messages)} messages for conversation {conversation_id}")
        # Debug: Log message IDs and order
        for i, msg in enumerate(messages):
            logger.info(f"Message {i}: ID={msg.id}, Role={msg.role}, Content={msg.content[:50]}...")
        return messages


    async def save_user_message(
        self,
        db: AsyncSession,
        user_id: int,
        content: str,
        conversation_id: Optional[str] = None
    ) -> Tuple[str, str]:
        """Process user message with AgentCore and return conversation ID and AI response."""
        logger.info(f"🤖 PROCESSING MESSAGE WITH AGENTCORE: user {user_id}, content: {content[:30]}...")
        
        # Let AgentCore handle all message saving and processing
        ai_response = await self.agent_core.run(content, user_id, enable_background_processing=False)
        
        # Get the conversation ID that AgentCore used
        from personal_assistant.memory.conversation_manager import get_conversation_id
        current_conversation_id = await get_conversation_id(user_id)
        
        if not current_conversation_id:
            raise ValueError("Failed to get conversation ID from AgentCore")
        
        logger.info(f"✅ MESSAGE PROCESSED BY AGENTCORE: conversation {current_conversation_id}, user {user_id}")
        
        return current_conversation_id, ai_response

    async def process_ai_response_background(
        self,
        db: Optional[AsyncSession],
        user_id: int,
        content: str,
        conversation_id: str
    ):
        """Process AI response in background to avoid timeout."""
        logger.info(f"🚀 STARTING AI BACKGROUND TASK: conversation {conversation_id}, user {user_id}")
        
        # Wait for user message to be fully committed
        import asyncio
        await asyncio.sleep(0.5)  # Increased delay
        
        # Verify user message exists before processing AI response
        from personal_assistant.database.session import AsyncSessionLocal
        async with AsyncSessionLocal() as check_db:
            check_query = select(ConversationMessage).where(
                ConversationMessage.conversation_id == conversation_id,
                ConversationMessage.role == "user"
            ).order_by(ConversationMessage.id.desc()).limit(1)
            check_result = await check_db.execute(check_query)
            latest_user_message = check_result.scalar_one_or_none()
            
            if not latest_user_message:
                logger.error(f"❌ USER MESSAGE NOT FOUND: conversation {conversation_id}")
                return
            else:
                logger.info(f"✅ USER MESSAGE VERIFIED: ID={latest_user_message.id}, Content={latest_user_message.content[:30]}...")
        
        # Create a new database session for the background task
        from personal_assistant.database.session import AsyncSessionLocal
        
        async with AsyncSessionLocal() as background_db:
            try:
                logger.info(f"🤖 PROCESSING AI RESPONSE: conversation {conversation_id}, user {user_id}")
                
                # Get AI response using AgentCore
                ai_response = await self.agent_core.run(content, user_id)
                logger.info(f"Received AI response: {ai_response[:100]}...")

                # Save AI response
                ai_message = ConversationMessage(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=ai_response,
                    message_type="assistant_response"
                )
                background_db.add(ai_message)
                
                # Update conversation
                conv_query = select(ConversationState).where(
                    ConversationState.conversation_id == conversation_id,
                    ConversationState.user_id == user_id
                )
                conv_result = await background_db.execute(conv_query)
                conversation = conv_result.scalar_one_or_none()
                
                if conversation:
                    conversation.user_input = content
                    conversation.step_count += 1
                    conversation.updated_at = datetime.utcnow()
                
                await background_db.commit()
                await background_db.refresh(ai_message)

                logger.info(f"✅ AI MESSAGE SAVED: conversation {conversation_id}, ID={ai_message.id}, Role={ai_message.role}, Content={ai_message.content[:30]}...")
                
            except Exception as e:
                await background_db.rollback()
                logger.error(f"Error processing AI response in background: {e}")
            # Save error message
            try:
                error_message = ConversationMessage(
                    conversation_id=conversation_id,
                    role="assistant",
                    content="I'm sorry, I encountered an error processing your message. Please try again.",
                    message_type="assistant_response"
                )
                db.add(error_message)
                await db.commit()
            except Exception as db_error:
                logger.error(f"Error saving error message: {db_error}")

    async def delete_conversation(self, db: AsyncSession, conversation_id: str, user_id: int) -> bool:
        """Delete a conversation."""
        conv_query = select(ConversationState).where(
            ConversationState.conversation_id == conversation_id,
            ConversationState.user_id == user_id
        )
        conv_result = await db.execute(conv_query)
        conversation = conv_result.scalar_one_or_none()
        
        if not conversation:
            return False

        await db.delete(conversation)
        await db.commit()
        
        logger.info(f"Deleted conversation {conversation_id} for user {user_id}")
        return True

    async def get_conversation_by_id(self, db: AsyncSession, conversation_id: str, user_id: int) -> Optional[ConversationState]:
        """Get a specific conversation by ID."""
        query = select(ConversationState).where(
            ConversationState.conversation_id == conversation_id,
            ConversationState.user_id == user_id
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

