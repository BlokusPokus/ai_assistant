"""
Segmentation Engine for Enhanced Todo Tool.

This module provides intelligent task segmentation using LLM to break down complex tasks
into manageable subtasks when users repeatedly miss deadlines.
"""

from datetime import datetime, timedelta
import select
from typing import List, Dict, Any, Optional
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from personal_assistant.database.models.todos import Todo
from personal_assistant.config.logging_config import get_logger

logger = get_logger("segmentation_engine")


class SegmentationEngine:
    """Intelligent task segmentation using LLM."""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.llm_client = None  # Will be initialized when needed
    
    async def segment_task(self, todo: Todo) -> List[Todo]:
        """
        Break down a complex task into manageable subtasks.
        
        Args:
            todo: Todo object to segment
            
        Returns:
            List of created subtasks
        """
        try:
            # Check if task can be segmented
            if not todo.can_be_segmented():
                logger.warning(f"Todo {todo.id} cannot be segmented (already segmented or not eligible)")
                return []
            
            # Create segmentation prompt
            prompt = self.create_segmentation_prompt(todo)
            
            # Get LLM response
            llm_response = await self.get_llm_response(prompt)
            
            # Parse response and create subtasks
            subtasks_data = self.parse_llm_response(llm_response)
            subtasks = await self.create_subtasks(todo, subtasks_data)
            
            # Mark original task as segmented
            todo.is_segmented = True
            todo.segmentation_triggered_at = datetime.utcnow()
            await self.db.commit()
            
            logger.info(f"Successfully segmented todo {todo.id} into {len(subtasks)} subtasks")
            return subtasks
            
        except Exception as e:
            logger.error(f"Error segmenting task {todo.id}: {e}")
            return []
    
    def create_segmentation_prompt(self, todo: Todo) -> str:
        """
        Create a prompt for LLM to segment the task.
        
        Args:
            todo: Todo object to segment
            
        Returns:
            Formatted prompt string
        """
        return f"""
You are an expert productivity coach specializing in helping people with ADHD break down overwhelming tasks.

Task to segment:
Title: {todo.title}
Description: {todo.description or 'No description provided'}
Due Date: {todo.due_date.strftime('%Y-%m-%d') if todo.due_date else 'No due date'}
Priority: {todo.priority}
Category: {todo.category or 'General'}
Missed Count: {todo.missed_count} times

This task has been missed {todo.missed_count} times, indicating it may be too complex or overwhelming. Please break this task down into 3-5 manageable subtasks that are:

1. Specific and actionable
2. Small enough to complete in 1-2 hours each
3. Ordered logically (some may depend on others)
4. Clear and easy to understand
5. Motivating and achievable for someone with ADHD

Format your response as a JSON array with this structure:
[
    {{
        "title": "Subtask title",
        "description": "Detailed description of what needs to be done",
        "estimated_duration": "1-2 hours",
        "priority": "high/medium/low",
        "order": 1
    }}
]

Focus on making each subtask feel achievable and motivating for someone with ADHD.
"""
    
    async def get_llm_response(self, prompt: str) -> str:
        """
        Get response from LLM for task segmentation.
        
        Args:
            prompt: Prompt to send to LLM
            
        Returns:
            LLM response string
        """
        try:
            # Import LLM client when needed to avoid circular imports
            if not self.llm_client:
                from personal_assistant.llm.gemini_client import GeminiClient
                self.llm_client = GeminiClient()
            
            # For now, return a mock response for testing
            # TODO: Replace with actual LLM call
            return self.get_mock_llm_response(prompt)
            
        except Exception as e:
            logger.error(f"Error getting LLM response: {e}")
            return self.get_mock_llm_response(prompt)
    
    def get_mock_llm_response(self, prompt: str) -> str:
        """
        Get mock LLM response for testing.
        
        Args:
            prompt: Original prompt
            
        Returns:
            Mock JSON response
        """
        # Extract task title from prompt
        lines = prompt.split('\n')
        title_line = next((line for line in lines if line.startswith('Title:')), 'Unknown Task')
        task_title = title_line.replace('Title:', '').strip()
        
        return f"""[{{
        "title": "Research and gather information",
        "description": "Spend 30 minutes researching the topic and gathering all necessary information and resources",
        "estimated_duration": "30 minutes",
        "priority": "high",
        "order": 1
    }}, {{
        "title": "Create initial outline",
        "description": "Create a basic outline or structure for the task based on the research",
        "estimated_duration": "45 minutes",
        "priority": "high",
        "order": 2
    }}, {{
        "title": "Execute main work",
        "description": "Complete the main part of the task following the outline",
        "estimated_duration": "1-2 hours",
        "priority": "medium",
        "order": 3
    }}, {{
        "title": "Review and finalize",
        "description": "Review the completed work, make any necessary adjustments, and finalize",
        "estimated_duration": "30 minutes",
        "priority": "medium",
        "order": 4
    }}]"""
    
    def parse_llm_response(self, response: str) -> List[Dict[str, Any]]:
        """
        Parse LLM response into subtask data.
        
        Args:
            response: LLM response string
            
        Returns:
            List of subtask dictionaries
        """
        try:
            import json
            
            # Extract JSON from response
            start = response.find('[')
            end = response.rfind(']') + 1
            
            if start == -1 or end == 0:
                logger.error("No JSON array found in LLM response")
                return []
            
            json_str = response[start:end]
            subtasks_data = json.loads(json_str)
            
            # Validate subtasks data
            validated_subtasks = []
            for i, subtask in enumerate(subtasks_data):
                if isinstance(subtask, dict) and 'title' in subtask:
                    validated_subtasks.append({
                        'title': subtask.get('title', f'Subtask {i+1}'),
                        'description': subtask.get('description', ''),
                        'estimated_duration': subtask.get('estimated_duration', '1 hour'),
                        'priority': subtask.get('priority', 'medium'),
                        'order': subtask.get('order', i + 1)
                    })
            
            return validated_subtasks
            
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            return []
    
    async def create_subtasks(self, parent_todo: Todo, subtasks_data: List[Dict[str, Any]]) -> List[Todo]:
        """
        Create subtasks from parsed data.
        
        Args:
            parent_todo: Parent todo object
            subtasks_data: List of subtask data dictionaries
            
        Returns:
            List of created subtask Todo objects
        """
        subtasks = []
        
        try:
            for i, subtask_data in enumerate(subtasks_data):
                # Calculate due date for subtask
                due_date = self.calculate_subtask_due_date(parent_todo, i, len(subtasks_data))
                
                # Create subtask
                subtask = Todo(
                    user_id=parent_todo.user_id,
                    title=subtask_data.get('title', f'Subtask {i+1}'),
                    description=subtask_data.get('description', ''),
                    due_date=due_date,
                    priority=subtask_data.get('priority', 'medium'),
                    category=parent_todo.category,
                    status='pending',
                    parent_task_id=parent_todo.id,
                    created_at=datetime.utcnow()
                )
                
                self.db.add(subtask)
                subtasks.append(subtask)
            
            await self.db.commit()
            logger.info(f"Created {len(subtasks)} subtasks for parent todo {parent_todo.id}")
            return subtasks
            
        except Exception as e:
            logger.error(f"Error creating subtasks: {e}")
            await self.db.rollback()
            return []
    
    def calculate_subtask_due_date(self, parent_todo: Todo, subtask_index: int, total_subtasks: int) -> datetime:
        """
        Calculate appropriate due date for subtask.
        
        Args:
            parent_todo: Parent todo object
            subtask_index: Index of this subtask (0-based)
            total_subtasks: Total number of subtasks
            
        Returns:
            Calculated due date for the subtask
        """
        if not parent_todo.due_date:
            # If no parent due date, spread subtasks over next few days
            return datetime.utcnow() + timedelta(days=subtask_index + 1)
        
        # Distribute subtasks evenly across remaining time
        time_remaining = parent_todo.due_date - datetime.utcnow()
        if time_remaining.total_seconds() <= 0:
            # If parent is already overdue, give each subtask 1 hour
            return datetime.utcnow() + timedelta(hours=subtask_index + 1)
        
        # Calculate time per subtask
        time_per_subtask = time_remaining / total_subtasks
        
        # Set due date for this subtask
        return datetime.utcnow() + (time_per_subtask * (subtask_index + 1))
    
    async def get_segmented_todos(self, user_id: int) -> List[Todo]:
        """
        Get all segmented todos for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of segmented todos
        """
        try:
            query = select(Todo).where(
                and_(
                    Todo.user_id == user_id,
                    Todo.is_segmented == True
                )
            )
            result = await self.db.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Error getting segmented todos for user {user_id}: {e}")
            return []
    
    async def get_subtasks(self, parent_todo_id: int) -> List[Todo]:
        """
        Get all subtasks for a parent todo.
        
        Args:
            parent_todo_id: ID of the parent todo
            
        Returns:
            List of subtasks
        """
        try:
            query = select(Todo).where(Todo.parent_task_id == parent_todo_id)
            result = await self.db.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Error getting subtasks for parent todo {parent_todo_id}: {e}")
            return []
