"""
Missed Counter Manager for Enhanced Todo Tool.

This module manages missed task counting and threshold detection for the todo system.
It tracks how many times tasks are missed and triggers auto-segmentation when thresholds are reached.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from personal_assistant.database.models.todos import Todo
from personal_assistant.config.logging_config import get_logger

logger = get_logger("missed_counter")


class MissedCounterManager:
    """Manages missed task counting and threshold detection."""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.default_threshold = 3  # Default threshold for auto-segmentation
    
    async def check_overdue_tasks(self, user_id: int, threshold: int = None) -> List[Todo]:
        """
        Check for overdue tasks and increment missed counters.
        
        Args:
            user_id: ID of the user whose tasks to check
            threshold: Custom threshold for auto-segmentation (defaults to 3)
            
        Returns:
            List of overdue todos that were processed
        """
        try:
            threshold = threshold or self.default_threshold
            
            # Get overdue tasks for user
            overdue_todos = await self.get_overdue_todos(user_id)
            
            processed_todos = []
            for todo in overdue_todos:
                await self.increment_missed_count(todo)
                processed_todos.append(todo)
                
                # Check if threshold reached
                if todo.missed_count >= threshold:
                    logger.info(f"Todo {todo.id} reached threshold {threshold}, triggering segmentation")
                    await self.trigger_segmentation(todo)
            
            logger.info(f"Processed {len(processed_todos)} overdue todos for user {user_id}")
            return processed_todos
            
        except Exception as e:
            logger.error(f"Error checking overdue tasks for user {user_id}: {e}")
            return []
    
    async def get_overdue_todos(self, user_id: int) -> List[Todo]:
        """
        Get todos that are overdue.
        
        Args:
            user_id: ID of the user whose overdue tasks to retrieve
            
        Returns:
            List of overdue todos
        """
        now = datetime.utcnow()
        query = select(Todo).where(
            and_(
                Todo.user_id == user_id,
                Todo.due_date < now,
                Todo.status.in_(['pending', 'in_progress'])
            )
        )
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def increment_missed_count(self, todo: Todo):
        """
        Increment missed count and update last_missed_at.
        
        Args:
            todo: Todo object to update
        """
        try:
            todo.missed_count += 1
            todo.last_missed_at = datetime.utcnow()
            
            # Update completion patterns for analytics
            await self.update_completion_patterns(todo)
            
            await self.db.commit()
            logger.info(f"Incremented missed count for todo {todo.id}: {todo.missed_count}")
            
        except Exception as e:
            logger.error(f"Error incrementing missed count for todo {todo.id}: {e}")
            await self.db.rollback()
    
    async def reset_missed_count(self, todo: Todo):
        """
        Reset missed count to 0.
        
        Args:
            todo: Todo object to reset
        """
        try:
            todo.missed_count = 0
            todo.last_missed_at = None
            
            await self.db.commit()
            logger.info(f"Reset missed count for todo {todo.id}")
            
        except Exception as e:
            logger.error(f"Error resetting missed count for todo {todo.id}: {e}")
            await self.db.rollback()
    
    async def get_tasks_approaching_threshold(self, user_id: int, threshold: int = None) -> List[Todo]:
        """
        Get tasks that are approaching the missed threshold.
        
        Args:
            user_id: ID of the user whose tasks to check
            threshold: Custom threshold (defaults to 3)
            
        Returns:
            List of todos approaching the threshold
        """
        threshold = threshold or self.default_threshold
        approaching_threshold = threshold - 1
        
        query = select(Todo).where(
            and_(
                Todo.user_id == user_id,
                Todo.missed_count >= approaching_threshold,
                Todo.status.in_(['pending', 'in_progress'])
            )
        )
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def trigger_segmentation(self, todo: Todo):
        """
        Trigger automatic segmentation for tasks with threshold+ missed attempts.
        
        Args:
            todo: Todo object to segment
        """
        try:
            # Import here to avoid circular imports
            from .segmentation_engine import SegmentationEngine
            
            segmentation_engine = SegmentationEngine(self.db)
            subtasks = await segmentation_engine.segment_task(todo)
            
            logger.info(f"Triggered segmentation for todo {todo.id}, created {len(subtasks)} subtasks")
            
        except Exception as e:
            logger.error(f"Error triggering segmentation for todo {todo.id}: {e}")
    
    async def update_completion_patterns(self, todo: Todo):
        """
        Update completion patterns for analytics.
        
        Args:
            todo: Todo object to update
        """
        try:
            if not todo.completion_patterns:
                todo.completion_patterns = {}
            
            patterns = todo.completion_patterns
            patterns['missed_dates'] = patterns.get('missed_dates', [])
            patterns['missed_dates'].append(datetime.utcnow().isoformat())
            patterns['total_missed'] = len(patterns['missed_dates'])
            patterns['last_updated'] = datetime.utcnow().isoformat()
            
            todo.completion_patterns = patterns
            
        except Exception as e:
            logger.error(f"Error updating completion patterns for todo {todo.id}: {e}")
    
    async def get_missed_tasks_summary(self, user_id: int) -> dict:
        """
        Get a summary of missed tasks for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Dictionary with missed tasks summary
        """
        try:
            # Get all todos for user
            query = select(Todo).where(Todo.user_id == user_id)
            result = await self.db.execute(query)
            all_todos = result.scalars().all()
            
            # Calculate statistics
            total_todos = len(all_todos)
            missed_todos = [t for t in all_todos if t.missed_count > 0]
            overdue_todos = [t for t in all_todos if t.is_overdue()]
            approaching_threshold = [t for t in all_todos if t.is_approaching_threshold()]
            
            return {
                'total_todos': total_todos,
                'missed_todos_count': len(missed_todos),
                'overdue_todos_count': len(overdue_todos),
                'approaching_threshold_count': len(approaching_threshold),
                'average_missed_count': sum(t.missed_count for t in missed_todos) / len(missed_todos) if missed_todos else 0,
                'high_miss_tasks': [t.title for t in missed_todos if t.missed_count >= self.default_threshold]
            }
            
        except Exception as e:
            logger.error(f"Error getting missed tasks summary for user {user_id}: {e}")
            return {}
