"""
AI Task Service - In-memory task management for AI agent operations.
"""

import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from personal_assistant.config.logging_config import get_logger
from .ai_task_models import AITask, TaskStatus, TaskComplexity

logger = get_logger("ai_task_service")


class AITaskService:
    """In-memory service for managing AI tasks within conversation sessions."""
    
    def __init__(self):
        """Initialize the AI task service."""
        self.tasks: Dict[str, AITask] = {}  # task_id -> AITask
        self.conversation_tasks: Dict[str, List[str]] = {}  # conversation_id -> [task_ids]
        self._lock = asyncio.Lock()
        
        # Session cleanup settings
        self.session_timeout = timedelta(hours=24)  # 24 hour timeout
        self._cleanup_task = None
        
        logger.info("AI Task Service initialized")
    
    async def create_task(
        self,
        content: str,
        conversation_id: str,
        complexity: TaskComplexity = TaskComplexity.SIMPLE,
        dependencies: Optional[List[str]] = None,
        parent_task_id: Optional[str] = None,
        ai_reasoning: Optional[str] = None
    ) -> AITask:
        """
        Create a new AI task.
        
        Args:
            content: Task description
            conversation_id: Associated conversation ID
            complexity: Task complexity level
            dependencies: List of task IDs this task depends on
            parent_task_id: Parent task ID for hierarchical organization
            ai_reasoning: AI's reasoning for creating this task
            
        Returns:
            Created AITask instance
            
        Raises:
            ValueError: If validation fails
        """
        async with self._lock:
            # Validate dependencies exist and are in same conversation
            if dependencies:
                for dep_id in dependencies:
                    if dep_id not in self.tasks:
                        raise ValueError(f"Dependency task {dep_id} not found")
                    
                    dep_task = self.tasks[dep_id]
                    if dep_task.conversation_id != conversation_id:
                        raise ValueError(f"Dependency task {dep_id} is from different conversation")
            
            # Create task
            task = AITask(
                content=content,
                conversation_id=conversation_id,
                complexity=complexity,
                dependencies=dependencies or [],
                parent_task_id=parent_task_id,
                ai_reasoning=ai_reasoning
            )
            
            # Store task
            self.tasks[task.id] = task
            
            # Add to conversation
            if conversation_id not in self.conversation_tasks:
                self.conversation_tasks[conversation_id] = []
            self.conversation_tasks[conversation_id].append(task.id)
            
            logger.info(f"Created AI task {task.id}: {content[:50]}...")
            return task
    
    async def get_task(self, task_id: str) -> Optional[AITask]:
        """Get a task by ID."""
        return self.tasks.get(task_id)
    
    async def get_tasks_by_conversation(self, conversation_id: str) -> List[AITask]:
        """Get all tasks for a conversation."""
        if conversation_id not in self.conversation_tasks:
            return []
        
        tasks = []
        for task_id in self.conversation_tasks[conversation_id]:
            task = self.tasks.get(task_id)
            if task:
                tasks.append(task)
            else:
                logger.warning(f"Task {task_id} not found in conversation {conversation_id}")
        
        return tasks
    
    async def get_all_tasks(self) -> List[AITask]:
        """Get all tasks across all conversations."""
        async with self._lock:
            return list(self.tasks.values())
    
    async def get_tasks_by_user(self, user_id: int) -> List[AITask]:
        """
        Get all tasks for a specific user.
        
        Note: This is a placeholder implementation. The current AI task system
        is conversation-based, not user-based. In a real implementation, you would
        need to:
        1. Store user_id with each task
        2. Query conversations by user_id
        3. Return tasks from those conversations
        
        For now, this returns all tasks as a temporary solution.
        """
        logger.warning(f"get_tasks_by_user called for user {user_id} - returning all tasks (conversation-based system)")
        return await self.get_all_tasks()
    
    async def update_task_status(self, task_id: str, status: TaskStatus) -> Optional[AITask]:
        """
        Update task status.
        
        Args:
            task_id: Task ID to update
            status: New status
            
        Returns:
            Updated AITask or None if not found
        """
        async with self._lock:
            task = self.tasks.get(task_id)
            if not task:
                logger.warning(f"Task {task_id} not found for status update")
                return None
            
            old_status = task.status
            task.update_status(status)
            
            logger.info(f"Updated task {task_id} status: {old_status.value} -> {status.value}")
            return task
    
    async def update_task_content(self, task_id: str, content: str) -> Optional[AITask]:
        """Update task content."""
        async with self._lock:
            task = self.tasks.get(task_id)
            if not task:
                logger.warning(f"Task {task_id} not found for content update")
                return None
            
            task.content = content
            task.updated_at = datetime.now()
            
            logger.info(f"Updated task {task_id} content")
            return task
    
    async def add_dependency(self, task_id: str, dependency_id: str) -> bool:
        """Add a dependency to a task."""
        async with self._lock:
            task = self.tasks.get(task_id)
            if not task:
                logger.warning(f"Task {task_id} not found for dependency addition")
                return False
            
            dep_task = self.tasks.get(dependency_id)
            if not dep_task:
                logger.warning(f"Dependency task {dependency_id} not found")
                return False
            
            if dep_task.conversation_id != task.conversation_id:
                logger.warning(f"Dependency task {dependency_id} is from different conversation")
                return False
            
            try:
                task.add_dependency(dependency_id)
                logger.info(f"Added dependency {dependency_id} to task {task_id}")
                return True
            except ValueError as e:
                logger.warning(f"Failed to add dependency: {e}")
                return False
    
    async def remove_dependency(self, task_id: str, dependency_id: str) -> bool:
        """Remove a dependency from a task."""
        async with self._lock:
            task = self.tasks.get(task_id)
            if not task:
                logger.warning(f"Task {task_id} not found for dependency removal")
                return False
            
            task.remove_dependency(dependency_id)
            logger.info(f"Removed dependency {dependency_id} from task {task_id}")
            return True
    
    async def delete_task(self, task_id: str) -> bool:
        """Delete a task and clean up references."""
        async with self._lock:
            task = self.tasks.get(task_id)
            if not task:
                logger.warning(f"Task {task_id} not found for deletion")
                return False
            
            # Remove from conversation
            if task.conversation_id in self.conversation_tasks:
                self.conversation_tasks[task.conversation_id].remove(task_id)
            
            # Remove task
            del self.tasks[task_id]
            
            logger.info(f"Deleted task {task_id}")
            return True
    
    async def get_ready_tasks(self, conversation_id: str) -> List[AITask]:
        """Get tasks that are ready to execute (dependencies completed)."""
        tasks = await self.get_tasks_by_conversation(conversation_id)
        ready_tasks = []
        
        for task in tasks:
            if task.status != TaskStatus.PENDING:
                continue
            
            # Check if all dependencies are completed
            all_deps_completed = True
            for dep_id in task.dependencies:
                dep_task = self.tasks.get(dep_id)
                if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                    all_deps_completed = False
                    break
            
            if all_deps_completed:
                ready_tasks.append(task)
        
        return ready_tasks
    
    async def get_next_task(self, conversation_id: str) -> Optional[AITask]:
        """Get the next task to execute (first ready task)."""
        ready_tasks = await self.get_ready_tasks(conversation_id)
        
        if not ready_tasks:
            return None
        
        # Return the first ready task (FIFO)
        return ready_tasks[0]
    
    async def clear_conversation(self, conversation_id: str) -> int:
        """Clear all tasks for a conversation."""
        async with self._lock:
            if conversation_id not in self.conversation_tasks:
                return 0
            
            task_count = len(self.conversation_tasks[conversation_id])
            
            # Remove all tasks
            for task_id in self.conversation_tasks[conversation_id]:
                if task_id in self.tasks:
                    del self.tasks[task_id]
            
            # Clear conversation
            del self.conversation_tasks[conversation_id]
            
            logger.info(f"Cleared {task_count} tasks for conversation {conversation_id}")
            return task_count
    
    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired conversation sessions."""
        async with self._lock:
            now = datetime.now()
            expired_conversations = []
            
            for conversation_id, task_ids in self.conversation_tasks.items():
                if not task_ids:
                    continue
                
                # Check oldest task in conversation
                oldest_task = None
                for task_id in task_ids:
                    task = self.tasks.get(task_id)
                    if task and (oldest_task is None or task.created_at < oldest_task.created_at):
                        oldest_task = task
                
                if oldest_task and (now - oldest_task.created_at) > self.session_timeout:
                    expired_conversations.append(conversation_id)
            
            # Clean up expired conversations
            total_tasks = 0
            for conversation_id in expired_conversations:
                task_count = await self.clear_conversation(conversation_id)
                total_tasks += task_count
            
            if total_tasks > 0:
                logger.info(f"Cleaned up {total_tasks} tasks from {len(expired_conversations)} expired sessions")
            
            return total_tasks
    
    def get_stats(self) -> dict:
        """Get service statistics."""
        total_tasks = len(self.tasks)
        total_conversations = len(self.conversation_tasks)
        
        status_counts = {}
        for task in self.tasks.values():
            status = task.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "total_tasks": total_tasks,
            "total_conversations": total_conversations,
            "status_counts": status_counts,
            "memory_usage": f"{len(str(self.tasks))} characters"
        }


# Global instance for the application
ai_task_service = AITaskService()
