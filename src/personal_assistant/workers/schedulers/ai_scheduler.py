"""
AI Task Scheduler

This module handles AI-specific task scheduling logic,
separated from the general task execution.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List

# Import the existing AI scheduler components
from ...tools.ai_scheduler.core.task_manager import AITaskManager

logger = logging.getLogger(__name__)


class AIScheduler:
    """Handles AI task scheduling and management."""

    def __init__(self):
        self.task_manager = AITaskManager()

    async def get_due_tasks(self, limit: int = 50) -> List[Any]:
        """Get AI tasks that are due for execution."""
        try:
            due_tasks = await self.task_manager.get_due_tasks(limit=limit)
            logger.info(f"Found {len(due_tasks)} due AI tasks")
            return due_tasks  # type: ignore
        except Exception as e:
            logger.error(f"Error getting due tasks: {e}")
            return []

    async def calculate_next_run(
        self, schedule_type: str, schedule_config: Dict[str, Any]
    ) -> datetime:
        """Calculate next run time for recurring AI tasks."""
        try:
            if schedule_type == "daily":
                return datetime.utcnow() + timedelta(days=1)
            elif schedule_type == "weekly":
                days_ahead = 7 - datetime.utcnow().weekday()
                return datetime.utcnow() + timedelta(days=days_ahead)
            elif schedule_type == "monthly":
                # Simple monthly calculation
                next_month = datetime.utcnow().replace(day=1) + timedelta(days=32)
                return next_month.replace(day=1)
            elif schedule_type == "custom":
                # Handle custom cron-like schedules
                return self._parse_custom_schedule(schedule_config)
            else:
                logger.warning(f"Unknown schedule type: {schedule_type}")
                return datetime.utcnow() + timedelta(hours=1)
        except Exception as e:
            logger.error(f"Error calculating next run time: {e}")
            return datetime.utcnow() + timedelta(hours=1)

    def _parse_custom_schedule(self, schedule_config: Dict[str, Any]) -> datetime:
        """Parse custom schedule configuration."""
        try:
            # This is a simplified parser - will be enhanced in Task 037.2
            if "cron" in schedule_config:
                # TODO: Implement cron parsing
                pass

            # Default to hourly if parsing fails
            return datetime.utcnow() + timedelta(hours=1)
        except Exception as e:
            logger.error(f"Error parsing custom schedule: {e}")
            return datetime.utcnow() + timedelta(hours=1)

    async def get_task_statistics(self) -> Dict[str, Any]:
        """Get statistics about AI tasks."""
        try:
            total_tasks = await self.task_manager.get_total_task_count()
            pending_tasks = await self.task_manager.get_pending_task_count()
            completed_tasks = await self.task_manager.get_completed_task_count()
            failed_tasks = await self.task_manager.get_failed_task_count()

            return {
                "total_tasks": total_tasks,
                "pending_tasks": pending_tasks,
                "completed_tasks": completed_tasks,
                "failed_tasks": failed_tasks,
                "success_rate": (completed_tasks / total_tasks * 100)
                if total_tasks > 0
                else 0,
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error getting task statistics: {e}")
            return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}

    async def cleanup_old_tasks(self, days_old: int = 30) -> int:
        """Clean up old completed/failed tasks."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            cleaned_count = await self.task_manager.cleanup_old_tasks(cutoff_date)
            logger.info(f"Cleaned up {cleaned_count} old AI tasks")
            return cleaned_count  # type: ignore
        except Exception as e:
            logger.error(f"Error cleaning up old tasks: {e}")
            return 0

    def get_schedule_info(self) -> Dict[str, Any]:
        """Get schedule information for test compatibility."""
        return {
            "type": "ai_scheduler",
            "status": "running",
            "version": "1.0.0",
            "task_manager": "AITaskManager",
        }


# Global AI scheduler instance
ai_scheduler = AIScheduler()
