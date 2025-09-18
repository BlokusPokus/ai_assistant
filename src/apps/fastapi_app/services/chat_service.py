"""
Chat Service for Task 073: Chat Integration with Agent Service.

This service handles chat conversation management, message processing,
and integration with the AgentCore service.
"""

import logging
from datetime import datetime
from typing import List, Optional, Tuple
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from personal_assistant.core import AgentCore
from personal_assistant.database.models.conversation_state import ConversationState
from personal_assistant.database.models.conversation_message import ConversationMessage
from personal_assistant.database.models.users import User

logger = logging.getLogger(__name__)


class ChatService:
    """Service for managing chat conversations and messages."""

    def __init__(self, agent_core: AgentCore):
        self.agent_core = agent_core

    async def create_conversation(self, db: AsyncSession, user_id: int) -> ConversationState:
        """Create a new conversation."""
        conversation_id = str(uuid4())
        conversation = ConversationState(
            conversation_id=conversation_id,
            user_id=user_id,
            user_input=None,  # Will be set when first message is sent
            focus_areas=None,
            step_count=0,
            last_tool_result=None
        )
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
        logger.info(f"Created new conversation {conversation_id} for user {user_id}")
        return conversation

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
            .order_by(ConversationMessage.timestamp.desc())
            .limit(limit)
        )
        result = await db.execute(query)
        messages = result.scalars().all()
        
        logger.info(f"Retrieved {len(messages)} messages for conversation {conversation_id}")
        return messages

    async def send_message(
        self,
        db: AsyncSession,
        user_id: int,
        content: str,
        conversation_id: Optional[str] = None
    ) -> Tuple[ConversationMessage, ConversationMessage, str]:
        """Send a message and get AI response."""
        # Get or create conversation
        if conversation_id:
            conv_query = select(ConversationState).where(
                ConversationState.conversation_id == conversation_id,
                ConversationState.user_id == user_id
            )
            conv_result = await db.execute(conv_query)
            conversation = conv_result.scalar_one_or_none()
            
            if not conversation:
                raise ValueError("Conversation not found or access denied")
        else:
            conversation = await self.create_conversation(db, user_id)
            conversation_id = conversation.conversation_id

        # Save user message
        user_message = ConversationMessage(
            conversation_id=conversation_id,
            role="user",
            content=content,
            message_type="user_input"
        )
        db.add(user_message)
        await db.commit()
        await db.refresh(user_message)

        logger.info(f"Saved user message for conversation {conversation_id}")

        # Get AI response using AgentCore
        try:
            logger.info(f"Getting AI response for user {user_id}")
            ai_response = await self.agent_core.run(content, user_id)
            logger.info(f"Received AI response: {ai_response[:100]}...")
        except Exception as e:
            logger.error(f"Error getting AI response: {e}")
            ai_response = "I'm sorry, I encountered an error processing your message. Please try again."

        # Save AI response
        ai_message = ConversationMessage(
            conversation_id=conversation_id,
            role="assistant",
            content=ai_response,
            message_type="assistant_response"
        )
        db.add(ai_message)
        
        # Update conversation with user input and increment step count
        conversation.user_input = content
        conversation.step_count += 1
        conversation.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(ai_message)

        logger.info(f"Saved AI response for conversation {conversation_id}")
        return user_message, ai_message, conversation_id

    async def save_user_message(
        self,
        db: AsyncSession,
        user_id: int,
        content: str,
        conversation_id: Optional[str] = None
    ) -> Tuple[ConversationMessage, str]:
        """Save user message and return conversation ID."""
        # Get or create conversation
        if conversation_id:
            conv_query = select(ConversationState).where(
                ConversationState.conversation_id == conversation_id,
                ConversationState.user_id == user_id
            )
            conv_result = await db.execute(conv_query)
            conversation = conv_result.scalar_one_or_none()
            
            if not conversation:
                raise ValueError("Conversation not found or access denied")
        else:
            conversation = await self.create_conversation(db, user_id)
            conversation_id = conversation.conversation_id

        # Save user message
        user_message = ConversationMessage(
            conversation_id=conversation_id,
            role="user",
            content=content,
            message_type="user_input"
        )
        db.add(user_message)
        await db.commit()
        await db.refresh(user_message)

        logger.info(f"Saved user message for conversation {conversation_id}")
        return user_message, conversation_id

    async def process_ai_response_background(
        self,
        db: AsyncSession,
        user_id: int,
        content: str,
        conversation_id: str
    ):
        """Process AI response in background to avoid timeout."""
        try:
            logger.info(f"Processing AI response in background for user {user_id}")
            
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
            db.add(ai_message)
            
            # Update conversation
            conv_query = select(ConversationState).where(
                ConversationState.conversation_id == conversation_id,
                ConversationState.user_id == user_id
            )
            conv_result = await db.execute(conv_query)
            conversation = conv_result.scalar_one_or_none()
            
            if conversation:
                conversation.user_input = content
                conversation.step_count += 1
                conversation.updated_at = datetime.utcnow()
            
            await db.commit()
            await db.refresh(ai_message)

            logger.info(f"Successfully processed AI response for conversation {conversation_id}")
            
        except Exception as e:
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

