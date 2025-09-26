"""
AI Task Service Integration - Service for integrating AI task management with AgentCore.
"""

from typing import Optional
from personal_assistant.config.logging_config import get_logger
from personal_assistant.tools.ai_tasks.ai_task_service import ai_task_service
from personal_assistant.tools.ai_tasks.ai_task_models import TaskStatus

logger = get_logger("ai_task_service_integration")


class AITaskServiceIntegration:
    """Service for integrating AI task management with AgentCore conversation flow."""
    
    def __init__(self):
        """Initialize the AI task service integration."""
        self.task_service = ai_task_service
        logger.info("AI Task Service Integration initialized")
    
    async def get_conversation_tasks(self, conversation_id: str) -> list:
        """Get all tasks for a conversation."""
        return await self.task_service.get_tasks_by_conversation(conversation_id)
    
    async def get_next_ready_task(self, conversation_id: str):
        """Get the next task ready for execution."""
        return await self.task_service.get_next_task(conversation_id)
    
    async def mark_task_in_progress(self, task_id: str) -> bool:
        """Mark a task as in progress."""
        task = await self.task_service.update_task_status(task_id, TaskStatus.IN_PROGRESS)
        return task is not None
    
    async def mark_task_completed(self, task_id: str) -> bool:
        """Mark a task as completed."""
        task = await self.task_service.update_task_status(task_id, TaskStatus.COMPLETED)
        return task is not None
    
    async def mark_task_cancelled(self, task_id: str) -> bool:
        """Mark a task as cancelled."""
        task = await self.task_service.update_task_status(task_id, TaskStatus.CANCELLED)
        return task is not None
    
    async def clear_conversation_tasks(self, conversation_id: str) -> int:
        """Clear all tasks for a conversation."""
        return await self.task_service.clear_conversation(conversation_id)
    
    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired conversation sessions."""
        return await self.task_service.cleanup_expired_sessions()
    
    def get_service_stats(self) -> dict:
        """Get AI task service statistics."""
        return self.task_service.get_stats()


