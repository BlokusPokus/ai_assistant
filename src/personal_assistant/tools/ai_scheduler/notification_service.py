"""
Notification Service for AI tasks.

This module handles sending notifications (SMS, email, etc.) when AI tasks
are executed or reminders are triggered.
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

# Import Twilio for SMS notifications
try:
    from twilio.base.exceptions import TwilioException
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    logging.warning("Twilio not available - SMS notifications disabled")

from ...database.models.ai_tasks import AITask

logger = logging.getLogger(__name__)


class NotificationService:
    """Handles notifications for AI tasks."""

    def __init__(self):
        self.logger = logger
        self.twilio_client = None
        self._initialize_twilio()

    def _initialize_twilio(self):
        """Initialize Twilio client if credentials are available."""
        if not TWILIO_AVAILABLE:
            return

        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        from_number = os.getenv('TWILIO_FROM_NUMBER')

        if account_sid and auth_token and from_number:
            try:
                self.twilio_client = Client(account_sid, auth_token)
                self.from_number = from_number
                self.logger.info("Twilio client initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize Twilio client: {e}")
                self.twilio_client = None
        else:
            self.logger.warning(
                "Twilio credentials not found - SMS notifications disabled")

    async def send_sms_notification(
        self,
        to_number: str,
        message: str,
        task_title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send SMS notification via Twilio.

        Args:
            to_number: Phone number to send to
            message: Message content
            task_title: Optional task title for context

        Returns:
            Dictionary with success status and details
        """
        if not self.twilio_client:
            return {
                'success': False,
                'error': 'Twilio client not available',
                'channel': 'sms'
            }

        try:
            # Format message with task context if available
            if task_title:
                formatted_message = f"[AI Task: {task_title}]\n\n{message}"
            else:
                formatted_message = message

            # Truncate message to fit Twilio's 1600 character limit
            # Leave some buffer for potential encoding issues
            max_length = 1500
            if len(formatted_message) > max_length:
                # Truncate and add indicator
                truncated_message = formatted_message[:max_length-3] + "..."
                self.logger.warning(
                    f"SMS message truncated from {len(formatted_message)} to {len(truncated_message)} characters")
                formatted_message = truncated_message

            # Send SMS via Twilio
            message_obj = self.twilio_client.messages.create(
                body=formatted_message,
                from_=self.from_number,
                to=to_number
            )

            self.logger.info(f"SMS sent successfully: {message_obj.sid}")
            return {
                'success': True,
                'message_sid': message_obj.sid,
                'channel': 'sms',
                'to': to_number
            }

        except TwilioException as e:
            self.logger.error(f"Twilio SMS error: {e}")
            return {
                'success': False,
                'error': str(e),
                'channel': 'sms'
            }
        except Exception as e:
            self.logger.error(f"Unexpected SMS error: {e}")
            return {
                'success': False,
                'error': str(e),
                'channel': 'sms'
            }

    async def send_task_completion_notification(
        self,
        task: 'AITask',
        result: Dict[str, Any],
        user_phone: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send notification when a task is completed.

        Args:
            task: The completed task
            result: Task execution result
            user_phone: User's phone number

        Returns:
            Notification result
        """
        if not user_phone:
            return {
                'success': False,
                'error': 'No phone number provided',
                'channel': 'sms'
            }

        # Create notification message
        message = self._format_task_completion_message(task, result)

        return await self.send_sms_notification(
            to_number=user_phone,
            message=message,
            task_title=task.title
        )

    async def send_reminder_notification(
        self,
        task: 'AITask',
        user_phone: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send reminder notification.

        Args:
            task: The reminder task
            user_phone: User's phone number

        Returns:
            Notification result
        """
        if not user_phone:
            return {
                'success': False,
                'error': 'No phone number provided',
                'channel': 'sms'
            }

        # Create reminder message
        message = self._format_reminder_message(task)

        return await self.send_sms_notification(
            to_number=user_phone,
            message=message,
            task_title=task.title
        )

    def _format_task_completion_message(self, task: 'AITask', result: Dict[str, Any]) -> str:
        """Format task completion message."""
        status = result.get('status', 'completed')
        message = result.get('message', 'Task completed')

        # Truncate long AI responses to prevent SMS character limit issues
        max_message_length = 500  # Leave room for formatting
        if len(message) > max_message_length:
            message = message[:max_message_length-3] + "..."

        if status == 'success':
            return f"✅ {task.title}\n\n{message}"
        elif status == 'failed':
            error = result.get('error', 'Unknown error')
            return f"❌ {task.title}\n\nFailed: {error}"
        else:
            return f"ℹ️ {task.title}\n\n{message}"

    def _format_reminder_message(self, task: 'AITask') -> str:
        """Format reminder message."""
        if task.description:
            return f"⏰ Reminder: {task.title}\n\n{task.description}"
        else:
            return f"⏰ Reminder: {task.title}"

    async def send_notification(
        self,
        channels: List[str],
        message: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send notification through multiple channels.

        Args:
            channels: List of notification channels
            message: Message content
            **kwargs: Additional parameters (to_number, task_title, etc.)

        Returns:
            Dictionary with results for each channel
        """
        results = {}

        for channel in channels:
            if channel == 'sms':
                to_number = kwargs.get('to_number')
                task_title = kwargs.get('task_title')

                if to_number:
                    results['sms'] = await self.send_sms_notification(
                        to_number=to_number,
                        message=message,
                        task_title=task_title
                    )
                else:
                    results['sms'] = {
                        'success': False,
                        'error': 'No phone number provided',
                        'channel': 'sms'
                    }

            elif channel == 'email':
                # TODO: Implement email notifications
                results['email'] = {
                    'success': False,
                    'error': 'Email notifications not implemented yet',
                    'channel': 'email'
                }

            elif channel == 'in_app':
                # TODO: Implement in-app notifications
                results['in_app'] = {
                    'success': False,
                    'error': 'In-app notifications not implemented yet',
                    'channel': 'in_app'
                }

            else:
                results[channel] = {
                    'success': False,
                    'error': f'Unknown notification channel: {channel}',
                    'channel': channel
                }

        return results

    def is_channel_available(self, channel: str) -> bool:
        """
        Check if a notification channel is available.

        Args:
            channel: Channel name

        Returns:
            True if available, False otherwise
        """
        if channel == 'sms':
            return self.twilio_client is not None
        elif channel == 'email':
            return False  # Not implemented yet
        elif channel == 'in_app':
            return False  # Not implemented yet
        else:
            return False

    def get_available_channels(self) -> List[str]:
        """
        Get list of available notification channels.

        Returns:
            List of available channels
        """
        channels = []

        if self.twilio_client:
            channels.append('sms')

        # Add other channels as they're implemented
        # channels.append('email')
        # channels.append('in_app')

        return channels
