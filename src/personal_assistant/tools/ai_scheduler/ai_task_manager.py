"""
AI Task Manager for handling AI-driven tasks and reminders.

This module provides functionality for creating, managing, and scheduling
AI tasks that can be executed by the AI assistant.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, select

from personal_assistant.database.models.ai_tasks import AITask
from personal_assistant.database.session import AsyncSessionLocal

logger = logging.getLogger(__name__)


class AITaskManager:
    """Manages AI tasks and reminders."""

    def __init__(self):
        self.logger = logger

    async def create_task(
        self,
        user_id: int,
        title: str,
        description: Optional[str] = None,
        task_type: str = "reminder",
        schedule_type: str = "once",
        schedule_config: Optional[Dict[str, Any]] = None,
        next_run_at: Optional[datetime] = None,
        ai_context: Optional[str] = None,
        notification_channels: Optional[List[str]] = None,
    ) -> AITask:
        """
        Create a new AI task.

        Args:
            user_id: User ID
            title: Task title
            description: Task description
            task_type: Type of task ('reminder', 'automated_task', 'periodic_task')
            schedule_type: Scheduling type ('once', 'daily', 'weekly', 'monthly', 'custom')
            schedule_config: Scheduling configuration (JSON)
            next_run_at: When to run the task next
            ai_context: Context for AI processing
            notification_channels: List of notification channels

        Returns:
            Created AITask instance
        """
        async with AsyncSessionLocal() as session:
            try:
                # Convert datetime objects in schedule_config to ISO format strings
                serialized_schedule_config = self._serialize_schedule_config(
                    schedule_config or {}
                )

                task = AITask(
                    user_id=user_id,
                    title=title,
                    description=description,
                    task_type=task_type,
                    schedule_type=schedule_type,
                    schedule_config=serialized_schedule_config,
                    next_run_at=next_run_at,
                    ai_context=ai_context,
                    notification_channels=notification_channels or ["sms"],
                )

                session.add(task)
                await session.commit()
                await session.refresh(task)

                self.logger.info(f"Created AI task: {task.title} (ID: {task.id})")
                return task

            except Exception as e:
                self.logger.error(f"Error creating AI task: {e}")
                await session.rollback()
                raise

    def _serialize_schedule_config(
        self, schedule_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Serialize schedule config by converting datetime objects to ISO format strings.

        Args:
            schedule_config: Original schedule configuration

        Returns:
            Serialized schedule configuration
        """
        serialized = {}
        for key, value in schedule_config.items():
            if isinstance(value, datetime):
                serialized[key] = value.isoformat()
            elif isinstance(value, dict):
                serialized[key] = self._serialize_schedule_config(value)
            elif isinstance(value, list):
                serialized[key] = [
                    item.isoformat() if isinstance(item, datetime) else item
                    for item in value
                ]
            else:
                serialized[key] = value
        return serialized

    async def get_due_tasks(self, limit: int = 50) -> List[AITask]:
        """
        Get tasks that are due for execution.

        Args:
            limit: Maximum number of tasks to return

        Returns:
            List of due tasks
        """
        async with AsyncSessionLocal() as session:
            try:
                result = await session.execute(
                    select(AITask)
                    .where(
                        and_(
                            AITask.status == "active",
                            AITask.next_run_at <= datetime.utcnow(),
                        )
                    )
                    .order_by(AITask.next_run_at.asc())
                    .limit(limit)
                )
                return result.scalars().all()

            except Exception as e:
                self.logger.error(f"Error getting due tasks: {e}")
                return []

    async def get_user_tasks(
        self,
        user_id: int,
        status: Optional[str] = None,
        task_type: Optional[str] = None,
        limit: int = 50,
    ) -> List[AITask]:
        """
        Get tasks for a specific user.

        Args:
            user_id: User ID
            status: Filter by status
            task_type: Filter by task type
            limit: Maximum number of tasks to return

        Returns:
            List of user tasks
        """
        async with AsyncSessionLocal() as session:
            try:
                query = select(AITask).where(AITask.user_id == user_id)

                if status:
                    query = query.where(AITask.status == status)
                if task_type:
                    query = query.where(AITask.task_type == task_type)

                query = query.order_by(AITask.created_at.desc()).limit(limit)
                result = await session.execute(query)
                return result.scalars().all()

            except Exception as e:
                self.logger.error(f"Error getting user tasks: {e}")
                return []

    async def update_task_status(
        self,
        task_id: int,
        status: str,
        last_run_at: Optional[datetime] = None,
        next_run_at: Optional[datetime] = None,
    ) -> bool:
        """
        Update task status and timing.

        Args:
            task_id: Task ID
            status: New status
            last_run_at: When the task was last run
            next_run_at: When the task should run next

        Returns:
            True if successful, False otherwise
        """
        async with AsyncSessionLocal() as session:
            try:
                result = await session.execute(
                    select(AITask).where(AITask.id == task_id)
                )
                task = result.scalar_one_or_none()

                if not task:
                    self.logger.warning(f"Task not found: {task_id}")
                    return False

                task.status = status
                if last_run_at:
                    task.last_run_at = last_run_at
                if next_run_at:
                    task.next_run_at = next_run_at

                await session.commit()
                self.logger.info(f"Updated task {task_id} status to {status}")
                return True

            except Exception as e:
                self.logger.error(f"Error updating task status: {e}")
                await session.rollback()
                return False

    async def delete_task(self, task_id: int, user_id: int) -> bool:
        """
        Delete a task.

        Args:
            task_id: Task ID
            user_id: User ID (for security)

        Returns:
            True if successful, False otherwise
        """
        async with AsyncSessionLocal() as session:
            try:
                result = await session.execute(
                    select(AITask).where(
                        and_(AITask.id == task_id, AITask.user_id == user_id)
                    )
                )
                task = result.scalar_one_or_none()

                if not task:
                    self.logger.warning(f"Task not found or unauthorized: {task_id}")
                    return False

                await session.delete(task)
                await session.commit()
                self.logger.info(f"Deleted task: {task_id}")
                return True

            except Exception as e:
                self.logger.error(f"Error deleting task: {e}")
                await session.rollback()
                return False

    async def calculate_next_run(
        self,
        schedule_type: str,
        schedule_config: Dict[str, Any],
        current_time: Optional[datetime] = None,
    ) -> Optional[datetime]:
        """
        Calculate the next run time based on schedule configuration.

        Args:
            schedule_type: Type of schedule
            schedule_config: Schedule configuration
            current_time: Current time (defaults to now)

        Returns:
            Next run time or None if invalid
        """
        if current_time is None:
            current_time = datetime.utcnow()

        try:
            if schedule_type == "once":
                # For one-time tasks, use the specified time
                return schedule_config.get("run_at")

            elif schedule_type == "daily":
                # Daily at specific time
                hour = schedule_config.get("hour", 9)
                minute = schedule_config.get("minute", 0)
                next_run = current_time.replace(
                    hour=hour, minute=minute, second=0, microsecond=0
                )

                if next_run <= current_time:
                    next_run += timedelta(days=1)
                return next_run

            elif schedule_type == "weekly":
                # Weekly on specific days at specific time
                weekdays = schedule_config.get("weekdays", [0])  # Monday = 0
                hour = schedule_config.get("hour", 9)
                minute = schedule_config.get("minute", 0)

                current_weekday = current_time.weekday()
                next_run = None

                for weekday in sorted(weekdays):
                    if weekday > current_weekday:
                        days_ahead = weekday - current_weekday
                        next_run = current_time + timedelta(days=days_ahead)
                        next_run = next_run.replace(
                            hour=hour, minute=minute, second=0, microsecond=0
                        )
                        break

                if next_run is None:
                    # Next occurrence is next week
                    days_ahead = 7 - current_weekday + weekdays[0]
                    next_run = current_time + timedelta(days=days_ahead)
                    next_run = next_run.replace(
                        hour=hour, minute=minute, second=0, microsecond=0
                    )

                return next_run

            elif schedule_type == "monthly":
                # Monthly on specific day
                day = schedule_config.get("day", 1)
                hour = schedule_config.get("hour", 9)
                minute = schedule_config.get("minute", 0)

                next_run = current_time.replace(
                    day=day, hour=hour, minute=minute, second=0, microsecond=0
                )

                if next_run <= current_time:
                    # Move to next month
                    if current_time.month == 12:
                        next_run = next_run.replace(year=current_time.year + 1, month=1)
                    else:
                        next_run = next_run.replace(month=current_time.month + 1)

                return next_run

            elif schedule_type == "custom":
                # Custom cron-like expression
                # This is a simplified implementation
                interval_minutes = schedule_config.get("interval_minutes", 60)
                return current_time + timedelta(minutes=interval_minutes)

            else:
                self.logger.warning(f"Unknown schedule type: {schedule_type}")
                return None

        except Exception as e:
            self.logger.error(f"Error calculating next run time: {e}")
            return None

    async def create_reminder(
        self,
        user_id: int,
        title: str,
        remind_at: datetime,
        description: Optional[str] = None,
        notification_channels: Optional[List[str]] = None,
    ) -> AITask:
        """
        Create a simple reminder.

        Args:
            user_id: User ID
            title: Reminder title
            remind_at: When to send the reminder
            description: Reminder description
            notification_channels: Notification channels

        Returns:
            Created reminder task
        """
        return await self.create_task(
            user_id=user_id,
            title=title,
            description=description,
            task_type="reminder",
            schedule_type="once",
            schedule_config={"run_at": remind_at},
            next_run_at=remind_at,
            notification_channels=notification_channels or ["sms"],
        )

    async def create_periodic_task(
        self,
        user_id: int,
        title: str,
        schedule_type: str,
        schedule_config: Dict[str, Any],
        description: Optional[str] = None,
        ai_context: Optional[str] = None,
        notification_channels: Optional[List[str]] = None,
    ) -> AITask:
        """
        Create a periodic automated task.

        Args:
            user_id: User ID
            title: Task title
            schedule_type: Schedule type
            schedule_config: Schedule configuration
            description: Task description
            ai_context: AI context
            notification_channels: Notification channels

        Returns:
            Created periodic task
        """
        next_run_at = await self.calculate_next_run(schedule_type, schedule_config)

        return await self.create_task(
            user_id=user_id,
            title=title,
            description=description,
            task_type="periodic_task",
            schedule_type=schedule_type,
            schedule_config=schedule_config,
            next_run_at=next_run_at,
            ai_context=ai_context,
            notification_channels=notification_channels or ["sms"],
        )

    # Enhanced reminder methods with validation and formatting
    async def create_reminder_with_validation(
        self, text: str, time: str, channel: Optional[str] = "sms", user_id: int = 126
    ) -> Dict[str, Any]:
        """
        Create a reminder with full validation and user-friendly interface.

        Args:
            text: Reminder text
            time: Time in ISO format (YYYY-MM-DDTHH:MM:SS)
            channel: Notification channel (sms, email, in_app)
            user_id: User ID

        Returns:
            Dict with success status and response message
        """
        try:
            # Validate input parameters
            validation_result = self._validate_reminder_inputs(
                text, time, channel, user_id
            )
            if not validation_result["is_valid"]:
                return {"success": False, "message": validation_result["error_msg"]}

            # Parse time
            remind_at = validation_result["remind_at"]
            channel = validation_result["channel"]
            user_id = validation_result["user_id"]

            # Create the reminder task
            task = await self.create_reminder(
                user_id=user_id,
                title=text,
                remind_at=remind_at,
                description=text,
                notification_channels=[channel],
            )

            return {
                "success": True,
                "message": self._format_reminder_response(text, remind_at, task.id),
                "task_id": task.id,
            }

        except Exception as e:
            self.logger.error(f"Error setting reminder: {e}")
            return {"success": False, "message": f"❌ Error setting reminder: {str(e)}"}

    async def list_user_reminders(
        self, status: Optional[str] = "active", user_id: int = 126
    ) -> Dict[str, Any]:
        """
        List user reminders with formatting.

        Args:
            status: Filter by status (active, completed, failed, paused)
            user_id: User ID

        Returns:
            Dict with success status and formatted response
        """
        try:
            # Validate status
            if status and status not in ["active", "completed", "failed", "paused"]:
                return {
                    "success": False,
                    "message": f"❌ Error: Invalid status '{status}'. Valid statuses are: active, completed, failed, paused",
                }

            # Get user's reminder tasks
            tasks = await self.get_user_tasks(
                user_id=user_id, status=status, task_type="reminder", limit=50
            )

            if not tasks:
                return {"success": True, "message": f"No {status} reminders found."}

            # Format the response
            result = self._format_reminder_list_header(status, len(tasks))
            for task in tasks:
                result += self._format_reminder_item(task)

            return {"success": True, "message": result}

        except Exception as e:
            self.logger.error(f"Error listing reminders: {e}")
            return {"success": False, "message": f"❌ Error listing reminders: {str(e)}"}

    async def delete_user_reminder(
        self, reminder_id: int, user_id: int = 126
    ) -> Dict[str, Any]:
        """
        Delete a user reminder with validation.

        Args:
            reminder_id: Reminder ID to delete
            user_id: User ID

        Returns:
            Dict with success status and response message
        """
        try:
            # Validate reminder_id
            try:
                reminder_id = int(reminder_id)
            except (ValueError, TypeError):
                return {
                    "success": False,
                    "message": f"❌ Error: reminder_id must be a valid integer, got '{reminder_id}'",
                }

            # Check if the reminder exists and belongs to the user
            user_tasks = await self.get_user_tasks(
                user_id=user_id, task_type="reminder", limit=100
            )

            if not any(task.id == reminder_id for task in user_tasks):
                return {
                    "success": False,
                    "message": f"❌ Reminder {reminder_id} not found or you don't have permission to delete it",
                }

            # Delete the task
            success = await self.delete_task(reminder_id, user_id)

            if success:
                return {
                    "success": True,
                    "message": f"✅ Reminder {reminder_id} deleted successfully",
                }
            else:
                return {
                    "success": False,
                    "message": f"❌ Failed to delete reminder {reminder_id}",
                }

        except Exception as e:
            self.logger.error(f"Error deleting reminder: {e}")
            return {"success": False, "message": f"❌ Error deleting reminder: {str(e)}"}

    # Private validation and formatting methods
    def _validate_reminder_inputs(
        self, text: str, time: str, channel: Optional[str], user_id: int
    ) -> Dict[str, Any]:
        """Validate reminder input parameters."""
        # Validate text
        if not text or not text.strip():
            return {
                "is_valid": False,
                "error_msg": "❌ Error: Reminder text cannot be empty",
            }

        # Validate time
        if not time or not time.strip():
            return {"is_valid": False, "error_msg": "❌ Error: Time cannot be empty"}

        # Parse time - try multiple formats
        remind_at = self._parse_time_string(time)
        if remind_at is None:
            return {
                "is_valid": False,
                "error_msg": f"❌ Error: Invalid time format '{time}'. Please use ISO format (YYYY-MM-DDTHH:MM:SS) or relative time (e.g., 'in 1 hour', 'tomorrow at 9am')",
            }

        # Validate channel
        valid_channels = ["sms", "email", "in_app"]
        if channel and channel not in valid_channels:
            return {
                "is_valid": False,
                "error_msg": f"❌ Error: Invalid channel '{channel}'. Valid channels are: {', '.join(valid_channels)}",
            }
        channel = channel if channel else "sms"

        # Validate user_id
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            return {
                "is_valid": False,
                "error_msg": f"❌ Error: user_id must be a valid integer, got '{user_id}'",
            }

        return {
            "is_valid": True,
            "remind_at": remind_at,
            "channel": channel,
            "user_id": user_id,
            "error_msg": None,
        }

    def _parse_time_string(self, time_str: str) -> Optional[datetime]:
        """Parse various time string formats into datetime object."""
        if not time_str:
            return None

        # Convert to string if it's not already
        if not isinstance(time_str, str):
            time_str = str(time_str)

        if not time_str.strip():
            return None

        time_str = time_str.strip().lower()
        now = datetime.now()

        try:
            # Try ISO format first
            if "t" in time_str or "-" in time_str:
                return datetime.fromisoformat(time_str)
        except ValueError:
            pass

        try:
            # Handle relative times
            if time_str.startswith("in "):
                # Parse "in X minutes/hours/days"
                parts = time_str[3:].split()
                if len(parts) >= 2:
                    amount = int(parts[0])
                    unit = parts[1]

                    if unit.startswith("minute"):
                        return now + timedelta(minutes=amount)
                    elif unit.startswith("hour"):
                        return now + timedelta(hours=amount)
                    elif unit.startswith("day"):
                        return now + timedelta(days=amount)
                    elif unit.startswith("week"):
                        return now + timedelta(weeks=amount)

            # Handle "tomorrow at X"
            if time_str.startswith("tomorrow"):
                tomorrow = now + timedelta(days=1)
                if " at " in time_str:
                    time_part = time_str.split(" at ")[1]
                    hour, minute = self._parse_time_part(time_part)
                    if hour is not None:
                        return tomorrow.replace(
                            hour=hour, minute=minute or 0, second=0, microsecond=0
                        )
                else:
                    return tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)

            # Handle "today at X"
            if time_str.startswith("today"):
                if " at " in time_str:
                    time_part = time_str.split(" at ")[1]
                    hour, minute = self._parse_time_part(time_part)
                    if hour is not None:
                        result = now.replace(
                            hour=hour, minute=minute or 0, second=0, microsecond=0
                        )
                        # If time has passed today, schedule for tomorrow
                        if result <= now:
                            result += timedelta(days=1)
                        return result

            # Handle simple time formats like "7:00", "7:00 AM", "19:00"
            hour, minute = self._parse_time_part(time_str)
            if hour is not None:
                result = now.replace(
                    hour=hour, minute=minute or 0, second=0, microsecond=0
                )
                # If time has passed today, schedule for tomorrow
                if result <= now:
                    result += timedelta(days=1)
                return result

        except (ValueError, IndexError):
            pass

        return None

    def _parse_time_part(self, time_part: str) -> tuple[Optional[int], Optional[int]]:
        """Parse time part like '7:00 AM' or '19:00' into hour and minute."""
        try:
            time_part = time_part.strip()

            # Handle AM/PM format
            is_pm = "pm" in time_part
            is_am = "am" in time_part

            if is_pm or is_am:
                time_part = time_part.replace("am", "").replace("pm", "").strip()

            if ":" in time_part:
                hour_str, minute_str = time_part.split(":")
                hour = int(hour_str)
                minute = int(minute_str)

                # Convert to 24-hour format
                if is_pm and hour != 12:
                    hour += 12
                elif is_am and hour == 12:
                    hour = 0

                return hour, minute
            else:
                # Just hour
                hour = int(time_part)
                if is_pm and hour != 12:
                    hour += 12
                elif is_am and hour == 12:
                    hour = 0
                return hour, 0

        except (ValueError, IndexError):
            return None, None

    def _format_reminder_response(
        self, text: str, remind_at: datetime, task_id: int
    ) -> str:
        """Format successful reminder creation response."""
        return f"✅ Reminder set: '{text}' for {remind_at.strftime('%Y-%m-%d %H:%M')} (ID: {task_id})"

    def _format_reminder_list_header(self, status: str, count: int) -> str:
        """Format reminder list header."""
        return f"📋 {status.title()} reminders ({count} found):\n\n"

    def _format_reminder_item(self, task: AITask) -> str:
        """Format individual reminder item for display."""
        status_emoji = self._get_status_emoji(task.status)
        next_run = self._format_next_run_time(task.next_run_at)

        result = f"{status_emoji} **{task.title}** (ID: {task.id})\n"
        result += f"   📅 Next run: {next_run}\n"
        result += f"   📝 Status: {task.status}\n"

        if task.description and task.description != task.title:
            result += f"   📄 Description: {task.description}\n"

        result += "\n"
        return result

    def _get_status_emoji(self, status: str) -> str:
        """Get appropriate emoji for reminder status."""
        emoji_map = {"active": "⏰", "completed": "✅", "failed": "❌", "paused": "⏸️"}
        return emoji_map.get(status, "📝")

    def _format_next_run_time(self, next_run_at) -> str:
        """Format next run time for display."""
        if next_run_at:
            return next_run_at.strftime("%Y-%m-%d %H:%M")
        return "No schedule"
