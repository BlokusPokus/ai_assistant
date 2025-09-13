"""
Enhanced Todo Tool with Missed Counter and Auto-Segmentation.

This module provides the main todo tool implementation with advanced features
for behavioral tracking and intelligent task management.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from personal_assistant.database.models.todos import Todo
from personal_assistant.database.session import AsyncSessionLocal
from personal_assistant.tools.base import Tool
from personal_assistant.config.logging_config import get_logger

logger = get_logger("todo_tool")


class TodoTool:
    """Enhanced todo tool with missed counter and segmentation features."""
    
    def __init__(self):
        pass
    
    async def create_todo(
        self,
        user_id: int,
        title: str,
        description: str = None,
        due_date: str = None,
        priority: str = "medium",
        category: str = None
    ) -> Dict[str, Any]:
        """
        Create a new todo.
        
        Args:
            user_id: ID of the user creating the todo
            title: Title of the todo
            description: Optional description
            due_date: Optional due date (string in ISO format)
            priority: Priority level (high, medium, low)
            category: Optional category
            
        Returns:
            Dictionary with created todo information
        """
        try:
            # Parse due_date string to datetime object
            parsed_due_date = None
            if due_date:
                try:
                    # Try parsing ISO format first
                    if 'T' in due_date:
                        parsed_due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                    else:
                        # Try parsing date only format
                        parsed_due_date = datetime.fromisoformat(due_date)
                except ValueError as e:
                    logger.warning(f"Failed to parse due_date '{due_date}': {e}")
                    return {
                        'success': False,
                        'error': f"Invalid date format: {due_date}. Please use YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS format.",
                        'message': "Failed to create todo due to invalid date format"
                    }
            
            async with AsyncSessionLocal() as db:
                todo = Todo(
                    user_id=user_id,
                    title=title,
                    description=description,
                    due_date=parsed_due_date,
                    priority=priority,
                    category=category,
                    status='pending',
                    created_at=datetime.utcnow()
                )
                
                db.add(todo)
                await db.commit()
                
                logger.info(f"Created todo {todo.id} for user {user_id}")
                return {
                    'success': True,
                    'todo': todo.as_dict(),
                    'message': f"Todo '{title}' created successfully"
                }
            
        except Exception as e:
            logger.error(f"Error creating todo for user {user_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': "Failed to create todo"
            }
    
    async def get_todos(
        self,
        user_id: int,
        status: str = None,
        category: str = None,
        priority: str = None,
        include_subtasks: bool = True
    ) -> Dict[str, Any]:
        """
        Get todos for a user with optional filtering.
        
        Args:
            user_id: ID of the user
            status: Optional status filter
            category: Optional category filter
            priority: Optional priority filter
            include_subtasks: Whether to include subtasks
            
        Returns:
            Dictionary with todos list
        """
        try:
            async with AsyncSessionLocal() as db:
                # Build query
                query = select(Todo).where(Todo.user_id == user_id)
                
                if not include_subtasks:
                    query = query.where(Todo.parent_task_id.is_(None))
                
                if status:
                    query = query.where(Todo.status == status)
                
                if category:
                    query = query.where(Todo.category == category)
                
                if priority:
                    query = query.where(Todo.priority == priority)
                
                # Order by created_at desc
                query = query.order_by(Todo.created_at.desc())
                
                result = await db.execute(query)
                todos = result.scalars().all()
                
                return {
                    'success': True,
                    'todos': [todo.as_dict() for todo in todos],
                    'count': len(todos)
                }
            
        except Exception as e:
            logger.error(f"Error getting todos for user {user_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'todos': [],
                'count': 0
            }
    
    async def update_todo(
        self,
        todo_id: int,
        user_id: int,
        title: str = None,
        description: str = None,
        due_date: datetime = None,
        priority: str = None,
        category: str = None,
        status: str = None
    ) -> Dict[str, Any]:
        """
        Update a todo.
        
        Args:
            todo_id: ID of the todo to update
            user_id: ID of the user (for security)
            title: New title (optional)
            description: New description (optional)
            due_date: New due date (optional)
            priority: New priority (optional)
            category: New category (optional)
            status: New status (optional)
            
        Returns:
            Dictionary with updated todo information
        """
        try:
            async with AsyncSessionLocal() as db:
                # Get todo
                query = select(Todo).where(
                    and_(Todo.id == todo_id, Todo.user_id == user_id)
                )
                result = await db.execute(query)
                todo = result.scalar_one_or_none()
                
                if not todo:
                    return {
                        'success': False,
                        'error': 'Todo not found',
                        'message': 'Todo not found or access denied'
                    }
                
                # Update fields
                if title is not None:
                    todo.title = title
                if description is not None:
                    todo.description = description
                if due_date is not None:
                    todo.due_date = due_date
                if priority is not None:
                    todo.priority = priority
                if category is not None:
                    todo.category = category
                if status is not None:
                    todo.status = status
                    if status == 'completed':
                        todo.done_date = datetime.utcnow()
                
                todo.updated_at = datetime.utcnow()
                await db.commit()
                
                logger.info(f"Updated todo {todo_id} for user {user_id}")
                return {
                    'success': True,
                    'todo': todo.as_dict(),
                    'message': f"Todo '{todo.title}' updated successfully"
                }
            
        except Exception as e:
            logger.error(f"Error updating todo {todo_id} for user {user_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': "Failed to update todo"
            }
    
    async def complete_todo(self, todo_id: int, user_id: int) -> Dict[str, Any]:
        """
        Mark a todo as completed.
        
        Args:
            todo_id: ID of the todo to complete
            user_id: ID of the user (for security)
            
        Returns:
            Dictionary with completion information
        """
        return await self.update_todo(
            todo_id=todo_id,
            user_id=user_id,
            status='completed'
        )
    
    async def delete_todo(self, todo_id: int, user_id: int) -> Dict[str, Any]:
        """
        Delete a todo.
        
        Args:
            todo_id: ID of the todo to delete
            user_id: ID of the user (for security)
            
        Returns:
            Dictionary with deletion information
        """
        try:
            async with AsyncSessionLocal() as db:
                # Get todo
                query = select(Todo).where(
                    and_(Todo.id == todo_id, Todo.user_id == user_id)
                )
                result = await db.execute(query)
                todo = result.scalar_one_or_none()
                
                if not todo:
                    return {
                        'success': False,
                        'error': 'Todo not found',
                        'message': 'Todo not found or access denied'
                    }
                
                # Delete todo (cascade will handle subtasks)
                await db.delete(todo)
                await db.commit()
                
                logger.info(f"Deleted todo {todo_id} for user {user_id}")
                return {
                    'success': True,
                    'message': f"Todo '{todo.title}' deleted successfully"
                }
            
        except Exception as e:
            logger.error(f"Error deleting todo {todo_id} for user {user_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': "Failed to delete todo"
            }
    
    async def get_overdue_todos(self, user_id: int) -> Dict[str, Any]:
        """
        Get overdue todos for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Dictionary with overdue todos
        """
        try:
            from .missed_counter import MissedCounterManager
            
            async with AsyncSessionLocal() as db:
                missed_manager = MissedCounterManager(db)
                
                overdue_todos = await missed_manager.get_overdue_todos(user_id)
                
                return {
                    'success': True,
                    'overdue_todos': [todo.as_dict() for todo in overdue_todos],
                    'count': len(overdue_todos)
                }
            
        except Exception as e:
            logger.error(f"Error getting overdue todos for user {user_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'overdue_todos': [],
                'count': 0
            }
    
    async def get_todo_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Get statistics about todos for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Dictionary with todo statistics
        """
        try:
            from .missed_counter import MissedCounterManager
            from .behavioral_analytics import BehavioralAnalytics
            
            async with AsyncSessionLocal() as db:
                # Get missed counter summary
                missed_manager = MissedCounterManager(db)
                missed_summary = await missed_manager.get_missed_tasks_summary(user_id)
                
                # Get behavioral analytics
                analytics = BehavioralAnalytics(db)
                patterns = await analytics.analyze_completion_patterns(user_id)
                
                return {
                    'success': True,
                    'missed_summary': missed_summary,
                    'behavioral_patterns': patterns
                }
            
        except Exception as e:
            logger.error(f"Error getting todo stats for user {user_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': "Failed to get todo statistics"
            }
    
    async def trigger_segmentation(self, todo_id: int, user_id: int) -> Dict[str, Any]:
        """
        Manually trigger segmentation for a todo.
        
        Args:
            todo_id: ID of the todo to segment
            user_id: ID of the user (for security)
            
        Returns:
            Dictionary with segmentation results
        """
        try:
            from .segmentation_engine import SegmentationEngine
            
            async with AsyncSessionLocal() as db:
                # Get todo
                query = select(Todo).where(
                    and_(Todo.id == todo_id, Todo.user_id == user_id)
                )
                result = await db.execute(query)
                todo = result.scalar_one_or_none()
                
                if not todo:
                    return {
                        'success': False,
                        'error': 'Todo not found',
                        'message': 'Todo not found or access denied'
                    }
                
                # Trigger segmentation
                segmentation_engine = SegmentationEngine(db)
                subtasks = await segmentation_engine.segment_task(todo)
                
                return {
                    'success': True,
                    'subtasks': [subtask.as_dict() for subtask in subtasks],
                    'subtasks_created': len(subtasks),
                    'message': f"Todo '{todo.title}' segmented into {len(subtasks)} subtasks"
                }
            
        except Exception as e:
            logger.error(f"Error triggering segmentation for todo {todo_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': "Failed to trigger segmentation"
            }
    
    async def get_analytics(self, user_id: int) -> Dict[str, Any]:
        """
        Get behavioral analytics for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Dictionary with analytics data
        """
        try:
            from .behavioral_analytics import BehavioralAnalytics
            
            async with AsyncSessionLocal() as db:
                analytics = BehavioralAnalytics(db)
                
                patterns = await analytics.analyze_completion_patterns(user_id)
                insights = await analytics.generate_insights(user_id)
                
                return {
                    'success': True,
                    'patterns': patterns,
                    'insights': insights,
                    'generated_at': datetime.utcnow().isoformat()
                }
            
        except Exception as e:
            logger.error(f"Error getting analytics for user {user_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': "Failed to get analytics"
            }


# Create tool instances for the registry
def create_todo_tools() -> List[Tool]:
    """Create todo tool instances for the registry."""
    todo_tool = TodoTool()
    
    tools = [
        # Basic CRUD operations
        Tool(
            name="create_todo",
            func=todo_tool.create_todo,
            description="Create a new todo with title, description, due date, priority, and category",
            parameters={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "integer",
                        "description": "ID of the user creating the todo"
                    },
                    "title": {
                        "type": "string",
                        "description": "Title of the todo"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional description of the todo"
                    },
                    "due_date": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Optional due date for the todo (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS format)"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["high", "medium", "low"],
                        "description": "Priority level of the todo"
                    },
                    "category": {
                        "type": "string",
                        "description": "Optional category for the todo"
                    }
                },
                "required": ["title"]
            }
        ).set_category("Todos"),
        
        Tool(
            name="get_todos",
            func=todo_tool.get_todos,
            description="Get todos for a user with optional filtering by status, category, or priority",
            parameters={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "integer",
                        "description": "ID of the user"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "completed", "cancelled"],
                        "description": "Optional status filter"
                    },
                    "category": {
                        "type": "string",
                        "description": "Optional category filter"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["high", "medium", "low"],
                        "description": "Optional priority filter"
                    },
                    "include_subtasks": {
                        "type": "boolean",
                        "description": "Whether to include subtasks in results"
                    }
                },
                "required": []
            }
        ).set_category("Todos"),
        
        Tool(
            name="update_todo",
            func=todo_tool.update_todo,
            description="Update a todo's title, description, due date, priority, category, or status",
            parameters={
                "type": "object",
                "properties": {
                    "todo_id": {
                        "type": "integer",
                        "description": "ID of the todo to update"
                    },
                    "user_id": {
                        "type": "integer",
                        "description": "ID of the user (for security)"
                    },
                    "title": {
                        "type": "string",
                        "description": "New title for the todo"
                    },
                    "description": {
                        "type": "string",
                        "description": "New description for the todo"
                    },
                    "due_date": {
                        "type": "string",
                        "format": "date-time",
                        "description": "New due date for the todo"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["high", "medium", "low"],
                        "description": "New priority for the todo"
                    },
                    "category": {
                        "type": "string",
                        "description": "New category for the todo"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "completed", "cancelled"],
                        "description": "New status for the todo"
                    }
                },
                "required": ["todo_id"]
            }
        ).set_category("Todos"),
        
        Tool(
            name="complete_todo",
            func=todo_tool.complete_todo,
            description="Mark a todo as completed",
            parameters={
                "type": "object",
                "properties": {
                    "todo_id": {
                        "type": "integer",
                        "description": "ID of the todo to complete"
                    },
                    "user_id": {
                        "type": "integer",
                        "description": "ID of the user (for security)"
                    }
                },
                "required": ["todo_id"]
            }
        ).set_category("Todos"),
        
        Tool(
            name="delete_todo",
            func=todo_tool.delete_todo,
            description="Delete a todo",
            parameters={
                "type": "object",
                "properties": {
                    "todo_id": {
                        "type": "integer",
                        "description": "ID of the todo to delete"
                    },
                    "user_id": {
                        "type": "integer",
                        "description": "ID of the user (for security)"
                    }
                },
                "required": ["todo_id"]
            }
        ).set_category("Todos"),
        
        # Advanced features
        Tool(
            name="get_overdue_todos",
            func=todo_tool.get_overdue_todos,
            description="Get todos that are overdue for a user",
            parameters={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "integer",
                        "description": "ID of the user"
                    }
                },
                "required": []
            }
        ).set_category("Todos"),
        
        Tool(
            name="get_todo_stats",
            func=todo_tool.get_todo_stats,
            description="Get statistics and behavioral patterns for a user's todos",
            parameters={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "integer",
                        "description": "ID of the user"
                    }
                },
                "required": []
            }
        ).set_category("Todos"),
        
        Tool(
            name="trigger_segmentation",
            func=todo_tool.trigger_segmentation,
            description="Manually trigger segmentation for a complex todo",
            parameters={
                "type": "object",
                "properties": {
                    "todo_id": {
                        "type": "integer",
                        "description": "ID of the todo to segment"
                    },
                    "user_id": {
                        "type": "integer",
                        "description": "ID of the user (for security)"
                    }
                },
                "required": ["todo_id"]
            }
        ).set_category("Todos"),
        
        Tool(
            name="get_analytics",
            func=todo_tool.get_analytics,
            description="Get behavioral analytics and insights for a user's productivity patterns",
            parameters={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "integer",
                        "description": "ID of the user"
                    }
                },
                "required": []
            }
        ).set_category("Todos")
    ]
    
    return tools
