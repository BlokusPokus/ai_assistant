"""
Chat API routes for Task 073: Chat Integration with Agent Service.

This module provides REST API endpoints for chat functionality,
including message sending, conversation management, and real-time communication.
"""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from apps.fastapi_app.models.chat import (
    ConversationListResponse,
    ConversationResponse,
    MessageCreate,
    MessageResponse,
    SendMessageResponse,
)
from apps.fastapi_app.services.chat_service import ChatService
from personal_assistant.core import AgentCore
from personal_assistant.database.models.users import User
from personal_assistant.database.session import AsyncSessionLocal

# Import the get_current_user function from auth routes
from apps.fastapi_app.routes.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


async def get_db():
    """Get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_chat_service() -> ChatService:
    """Get chat service instance."""
    from personal_assistant.tools import create_tool_registry
    tool_registry = create_tool_registry()
    agent_core = AgentCore(tools=tool_registry)
    return ChatService(agent_core)


@router.post("/messages", response_model=SendMessageResponse)
async def send_message(
    message_data: MessageCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    chat_service: ChatService = Depends(get_chat_service),
):
    """Send a message to the AI agent."""
    try:
        logger.info(f"User {current_user.id} sending message: {message_data.content[:50]}...")
        
        # Save user message immediately and get conversation
        user_message, conversation_id = await chat_service.save_user_message(
            db, current_user.id, message_data.content, message_data.conversation_id
        )

        # Process AI response in background to avoid timeout
        background_tasks.add_task(
            chat_service.process_ai_response_background,
            db, current_user.id, message_data.content, conversation_id
        )

        # Return immediate response with user message
        response = SendMessageResponse(
            user_message=MessageResponse.model_validate(user_message),
            ai_message=MessageResponse(
                id=0,  # Placeholder - will be updated when AI responds
                conversation_id=conversation_id,
                role="assistant",
                content="Processing your request...",
                message_type="assistant_response",
                timestamp=datetime.utcnow().isoformat()
            ),
            conversation_id=conversation_id
        )
        
        logger.info(f"Successfully queued message for user {current_user.id}")
        return response
        
    except ValueError as e:
        logger.warning(f"Validation error for user {current_user.id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error sending message for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to send message")


@router.get("/conversations", response_model=ConversationListResponse)
async def get_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    chat_service: ChatService = Depends(get_chat_service),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
):
    """Get user's conversations."""
    try:
        logger.info(f"Getting conversations for user {current_user.id}, page {page}")
        
        conversations, total = await chat_service.get_user_conversations(
            db, current_user.id, page, per_page
        )

        conversation_responses = []
        for conv in conversations:
            # Get message count for each conversation by querying the database
            from sqlalchemy import select, func
            from personal_assistant.database.models.conversation_message import ConversationMessage
            
            count_query = select(func.count(ConversationMessage.id)).where(
                ConversationMessage.conversation_id == conv.conversation_id
            )
            count_result = await db.execute(count_query)
            message_count = count_result.scalar() or 0
            
            conversation_responses.append(
                ConversationResponse(
                    id=conv.id,
                    conversation_id=conv.conversation_id,
                    user_id=conv.user_id,
                    user_input=conv.user_input,
                    focus_areas=conv.focus_areas,
                    step_count=conv.step_count,
                    last_tool_result=conv.last_tool_result,
                    created_at=conv.created_at,
                    updated_at=conv.updated_at,
                    message_count=message_count
                )
            )

        response = ConversationListResponse(
            conversations=conversation_responses,
            total=total,
            page=page,
            per_page=per_page
        )
        
        logger.info(f"Retrieved {len(conversations)} conversations for user {current_user.id}")
        return response
        
    except Exception as e:
        logger.error(f"Error getting conversations for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get conversations")


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    chat_service: ChatService = Depends(get_chat_service),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of messages to return"),
):
    """Get messages for a conversation."""
    try:
        logger.info(f"Getting messages for conversation {conversation_id}, user {current_user.id}")
        
        messages = await chat_service.get_conversation_messages(
            db, conversation_id, current_user.id, limit
        )

        message_responses = [MessageResponse.model_validate(msg) for msg in messages]
        
        logger.info(f"Retrieved {len(messages)} messages for conversation {conversation_id}")
        return message_responses
        
    except ValueError as e:
        logger.warning(f"Validation error for conversation {conversation_id}: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting messages for conversation {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get messages")


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    chat_service: ChatService = Depends(get_chat_service),
):
    """Delete a conversation."""
    try:
        logger.info(f"Deleting conversation {conversation_id} for user {current_user.id}")
        
        success = await chat_service.delete_conversation(db, conversation_id, current_user.id)
        if not success:
            raise HTTPException(status_code=404, detail="Conversation not found")

        logger.info(f"Successfully deleted conversation {conversation_id}")
        return {"message": "Conversation deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete conversation")


# WebSocket endpoint for real-time communication (placeholder for future implementation)
@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
):
    """WebSocket endpoint for real-time chat."""
    await websocket.accept()
    
    try:
        # TODO: Implement WebSocket authentication and real-time communication
        # This is a placeholder for future WebSocket implementation
        logger.info("WebSocket connection established")
        
        while True:
            data = await websocket.receive_text()
            logger.info(f"Received WebSocket message: {data}")
            await websocket.send_text(f"Echo: {data}")
            
    except WebSocketDisconnect:
        logger.info("WebSocket connection closed")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()
