"""
Task Executor for AI tasks.

This module handles the execution of AI tasks using the AI assistant.
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from ...database.models.ai_tasks import AITask

logger = logging.getLogger(__name__)


class TaskExecutor:
    """Executes AI tasks using the AI assistant."""

    def __init__(self):
        self.logger = logger

    async def execute_task(self, task: AITask) -> Dict[str, Any]:
        """
        Execute an AI task.

        Args:
            task: The AI task to execute

        Returns:
            Dictionary with execution results
        """
        try:
            self.logger.info(f"Executing task: {task.title} (ID: {task.id})")

            # Import AgentCore here to avoid circular imports
            from ...core import AgentCore

            # Create task context
            task_context = self._build_task_context(task)

            # Create AI prompt based on task type
            ai_prompt = self._create_ai_prompt(task, task_context)

            # Execute with AI assistant
            agent = AgentCore()
            response = await agent.run(ai_prompt, task.user_id)

            # Process the response
            result = self._process_ai_response(task, response)

            self.logger.info(f"Successfully executed task: {task.title}")
            return result

        except Exception as e:
            self.logger.error(f"Error executing task {task.id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to execute task: {e}",
                "timestamp": datetime.utcnow().isoformat(),
            }

    def _build_task_context(self, task: AITask) -> Dict[str, Any]:
        """
        Build context for task execution.

        Args:
            task: The AI task

        Returns:
            Task context dictionary
        """
        context = {
            "task_id": task.id,
            "title": task.title,
            "description": task.description,
            "task_type": task.task_type,
            "schedule_type": task.schedule_type,
            "ai_context": task.ai_context,
            "notification_channels": task.notification_channels or [],
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "last_run_at": task.last_run_at.isoformat() if task.last_run_at else None,
            "current_time": datetime.utcnow().isoformat(),
        }

        return context

    def _create_ai_prompt(self, task: AITask, context: Dict[str, Any]) -> str:
        """
        Create AI prompt for task execution.

        Args:
            task: The AI task
            context: Task context

        Returns:
            AI prompt string
        """
        if task.task_type == "reminder":
            return self._create_reminder_prompt(task, context)
        elif task.task_type == "periodic_task":
            return self._create_periodic_task_prompt(task, context)
        elif task.task_type == "automated_task":
            return self._create_automated_task_prompt(task, context)
        else:
            return self._create_generic_task_prompt(task, context)

    def _create_reminder_prompt(self, task: AITask, context: Dict[str, Any]) -> str:
        """Create prompt for reminder tasks."""
        prompt = f"""
You have a reminder task to execute:

REMINDER DETAILS:
- Title: {task.title}
- Description: {task.description or 'No description'}
- Task Type: Reminder
- Created: {context['created_at']}
- Current Time: {context['current_time']}

TASK CONTEXT:
{task.ai_context or 'No additional context provided'}

Please:
1. Acknowledge the reminder
2. Provide any relevant information or context
3. Suggest any actions that might be needed
4. Give a brief summary of what this reminder is about

Provide a helpful, actionable response for this reminder.
"""
        return prompt

    def _create_periodic_task_prompt(
        self, task: AITask, context: Dict[str, Any]
    ) -> str:
        """Create prompt for periodic tasks."""
        prompt = f"""
You have a periodic task to execute:

PERIODIC TASK DETAILS:
- Title: {task.title}
- Description: {task.description or 'No description'}
- Task Type: Periodic Task
- Schedule Type: {task.schedule_type}
- Schedule Config: {task.schedule_config}
- Last Run: {context['last_run_at'] or 'Never'}
- Current Time: {context['current_time']}

TASK CONTEXT:
{task.ai_context or 'No additional context provided'}

Please:
1. Execute the periodic task based on the context
2. Provide a summary of what was done
3. Note any important findings or actions taken
4. Suggest any follow-up actions if needed

Provide a detailed response about the task execution and results.
"""
        return prompt

    def _create_automated_task_prompt(
        self, task: AITask, context: Dict[str, Any]
    ) -> str:
        """Create prompt for automated tasks."""
        prompt = f"""
You have an automated task to execute:

AUTOMATED TASK DETAILS:
- Title: {task.title}
- Description: {task.description or 'No description'}
- Task Type: Automated Task
- Current Time: {context['current_time']}

TASK CONTEXT:
{task.ai_context or 'No additional context provided'}

Please:
1. Execute the automated task
2. Provide a detailed report of what was done
3. Note any important findings or issues
4. Suggest any follow-up actions if needed

Provide a comprehensive response about the automated task execution.
"""
        return prompt

    def _create_generic_task_prompt(self, task: AITask, context: Dict[str, Any]) -> str:
        """Create generic prompt for other task types."""
        prompt = f"""
You have a task to execute:

TASK DETAILS:
- Title: {task.title}
- Description: {task.description or 'No description'}
- Task Type: {task.task_type}
- Current Time: {context['current_time']}

TASK CONTEXT:
{task.ai_context or 'No additional context provided'}

Please:
1. Execute the task based on the context
2. Provide a summary of what was done
3. Note any important findings or actions taken
4. Suggest any follow-up actions if needed

Provide a helpful response about the task execution.
"""
        return prompt

    def _process_ai_response(self, task: AITask, ai_response: str) -> Dict[str, Any]:
        """
        Process the AI response and create execution result.

        Args:
            task: The executed task
            ai_response: Response from AI assistant

        Returns:
            Execution result dictionary
        """
        # Basic response processing
        # In the future, this could be enhanced to parse structured responses

        return {
            "success": True,
            "message": ai_response,
            "task_id": task.id,
            "task_title": task.title,
            "task_type": task.task_type,
            "execution_time": datetime.utcnow().isoformat(),
            "ai_response": ai_response,
        }

    async def execute_reminder_task(self, task: AITask) -> Dict[str, Any]:
        """
        Execute a reminder task specifically.

        Args:
            task: The reminder task

        Returns:
            Execution result
        """
        return await self.execute_task(task)

    async def execute_periodic_task(self, task: AITask) -> Dict[str, Any]:
        """
        Execute a periodic task specifically.

        Args:
            task: The periodic task

        Returns:
            Execution result
        """
        return await self.execute_task(task)

    async def execute_automated_task(self, task: AITask) -> Dict[str, Any]:
        """
        Execute an automated task specifically.

        Args:
            task: The automated task

        Returns:
            Execution result
        """
        return await self.execute_task(task)
