"""
AI Task Tool - Tool for AI agent to manage its own tasks.
"""

from typing import Any, Dict, List, Optional
from personal_assistant.config.logging_config import get_logger
from personal_assistant.tools.base import Tool
from .ai_task_service import ai_task_service
from .ai_task_models import AITask, TaskStatus, TaskComplexity

logger = get_logger("ai_task_tool")


class ConversationTaskTool:
    """Tool for AI agent to manage conversation-based tasks for complex SMS requests."""
    
    def __init__(self):
        self.conversation_task_tool = Tool(
            name="conversation_task_manager",
            func=self._run,
            description="CONVERSATION TASKS: Break down complex SMS requests into manageable steps. Use for multi-step AI operations during conversations (e.g., 'analyze my emails and tell me what to do'). Tasks are session-based and temporary.",
            parameters={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "Action to perform: create, update_status, update_content, add_dependency, remove_dependency, delete, get_tasks, get_next_task"
                    },
                    "conversation_id": {
                        "type": "string",
                        "description": "Conversation ID for session-based task management"
                    },
                    "task_id": {
                        "type": "string",
                        "description": "Task ID for operations that target specific tasks"
                    },
                    "content": {
                        "type": "string",
                        "description": "Task content/description"
                    },
                    "complexity": {
                        "type": "integer",
                        "description": "Task complexity level (1=simple, 5=expert)"
                    },
                    "status": {
                        "type": "string",
                        "description": "Task status: pending, in_progress, completed, cancelled"
                    },
                    "dependencies": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of task IDs this task depends on"
                    },
                    "dependency_id": {
                        "type": "string",
                        "description": "Task ID to add/remove as dependency"
                    },
                    "parent_task_id": {
                        "type": "string",
                        "description": "Parent task ID for hierarchical organization"
                    },
                    "ai_reasoning": {
                        "type": "string",
                        "description": "AI's reasoning for creating this task"
                    }
                },
                "required": ["action", "conversation_id"]
            }
        )
    
    def __iter__(self):
        """Makes the class iterable to return all tools"""
        return iter([self.conversation_task_tool])
    
    async def _run(
        self,
        action: str,
        conversation_id: str,
        task_id: Optional[str] = None,
        content: Optional[str] = None,
        complexity: Optional[int] = None,
        status: Optional[str] = None,
        dependencies: Optional[List[str]] = None,
        dependency_id: Optional[str] = None,
        parent_task_id: Optional[str] = None,
        ai_reasoning: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute AI task management operations.
        
        Args:
            action: Action to perform
            conversation_id: Conversation ID for session management
            task_id: Task ID for targeted operations
            content: Task content
            complexity: Task complexity level
            status: Task status
            dependencies: List of dependency task IDs
            dependency_id: Specific dependency task ID
            parent_task_id: Parent task ID
            ai_reasoning: AI reasoning for task creation
            
        Returns:
            Operation result
        """
        try:
            if action == "create":
                return await self._create_task(
                    conversation_id, content, complexity, dependencies, 
                    parent_task_id, ai_reasoning
                )
            
            elif action == "update_status":
                return await self._update_status(task_id, status)
            
            elif action == "update_content":
                return await self._update_content(task_id, content)
            
            elif action == "add_dependency":
                return await self._add_dependency(task_id, dependency_id)
            
            elif action == "remove_dependency":
                return await self._remove_dependency(task_id, dependency_id)
            
            elif action == "delete":
                return await self._delete_task(task_id)
            
            elif action == "get_tasks":
                return await self._get_tasks(conversation_id)
            
            elif action == "get_next_task":
                return await self._get_next_task(conversation_id)
            
            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {action}"
                }
        
        except Exception as e:
            logger.error(f"AI Task Tool error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _create_task(
        self,
        conversation_id: str,
        content: Optional[str],
        complexity: Optional[int],
        dependencies: Optional[List[str]],
        parent_task_id: Optional[str],
        ai_reasoning: Optional[str]
    ) -> Dict[str, Any]:
        """Create a new AI task."""
        if not content:
            return {
                "success": False,
                "error": "Content is required for task creation"
            }
        
        try:
            task_complexity = TaskComplexity(complexity) if complexity else TaskComplexity.SIMPLE
            
            task = await ai_task_service.create_task(
                content=content,
                conversation_id=conversation_id,
                complexity=task_complexity,
                dependencies=dependencies,
                parent_task_id=parent_task_id,
                ai_reasoning=ai_reasoning
            )
            
            return {
                "success": True,
                "task": task.to_dict(),
                "message": f"Created task '{content[:50]}...' with complexity {task_complexity.value}"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create task: {e}"
            }
    
    async def _update_status(self, task_id: Optional[str], status: Optional[str]) -> Dict[str, Any]:
        """Update task status."""
        if not task_id or not status:
            return {
                "success": False,
                "error": "Task ID and status are required"
            }
        
        try:
            task_status = TaskStatus(status)
            task = await ai_task_service.update_task_status(task_id, task_status)
            
            if task:
                return {
                    "success": True,
                    "task": task.to_dict(),
                    "message": f"Updated task {task_id} status to {status}"
                }
            else:
                return {
                    "success": False,
                    "error": f"Task {task_id} not found"
                }
        
        except ValueError as e:
            return {
                "success": False,
                "error": f"Invalid status: {e}"
            }
    
    async def _update_content(self, task_id: Optional[str], content: Optional[str]) -> Dict[str, Any]:
        """Update task content."""
        if not task_id or not content:
            return {
                "success": False,
                "error": "Task ID and content are required"
            }
        
        task = await ai_task_service.update_task_content(task_id, content)
        
        if task:
            return {
                "success": True,
                "task": task.to_dict(),
                "message": f"Updated task {task_id} content"
            }
        else:
            return {
                "success": False,
                "error": f"Task {task_id} not found"
            }
    
    async def _add_dependency(self, task_id: Optional[str], dependency_id: Optional[str]) -> Dict[str, Any]:
        """Add dependency to task."""
        if not task_id or not dependency_id:
            return {
                "success": False,
                "error": "Task ID and dependency ID are required"
            }
        
        success = await ai_task_service.add_dependency(task_id, dependency_id)
        
        if success:
            return {
                "success": True,
                "message": f"Added dependency {dependency_id} to task {task_id}"
            }
        else:
            return {
                "success": False,
                "error": f"Failed to add dependency {dependency_id} to task {task_id}"
            }
    
    async def _remove_dependency(self, task_id: Optional[str], dependency_id: Optional[str]) -> Dict[str, Any]:
        """Remove dependency from task."""
        if not task_id or not dependency_id:
            return {
                "success": False,
                "error": "Task ID and dependency ID are required"
            }
        
        success = await ai_task_service.remove_dependency(task_id, dependency_id)
        
        if success:
            return {
                "success": True,
                "message": f"Removed dependency {dependency_id} from task {task_id}"
            }
        else:
            return {
                "success": False,
                "error": f"Failed to remove dependency {dependency_id} from task {task_id}"
            }
    
    async def _delete_task(self, task_id: Optional[str]) -> Dict[str, Any]:
        """Delete task."""
        if not task_id:
            return {
                "success": False,
                "error": "Task ID is required"
            }
        
        success = await ai_task_service.delete_task(task_id)
        
        if success:
            return {
                "success": True,
                "message": f"Deleted task {task_id}"
            }
        else:
            return {
                "success": False,
                "error": f"Task {task_id} not found"
            }
    
    async def _get_tasks(self, conversation_id: str) -> Dict[str, Any]:
        """Get all tasks for conversation."""
        tasks = await ai_task_service.get_tasks_by_conversation(conversation_id)
        
        return {
            "success": True,
            "tasks": [task.to_dict() for task in tasks],
            "count": len(tasks),
            "message": f"Retrieved {len(tasks)} tasks for conversation {conversation_id}"
        }
    
    async def _get_next_task(self, conversation_id: str) -> Dict[str, Any]:
        """Get next task ready for execution."""
        task = await ai_task_service.get_next_task(conversation_id)
        
        if task:
            return {
                "success": True,
                "task": task.to_dict(),
                "message": f"Next task ready: '{task.content[:50]}...'"
            }
        else:
            return {
                "success": True,
                "task": None,
                "message": "No tasks ready for execution"
            }
