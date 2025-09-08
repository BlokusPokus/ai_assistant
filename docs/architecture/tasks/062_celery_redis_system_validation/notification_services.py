# """
# Notification services for SMS and email actions.

# This module provides services for sending SMS and email notifications
# by integrating with existing Twilio and email systems.
# """

# import logging
# import os
# from datetime import datetime
# from typing import Any, Dict, Optional

# logger = logging.getLogger(__name__)


# class SMSService:
#     """
#     SMS service using Twilio integration.

#     This service integrates with the existing Twilio setup in the FastAPI app.
#     """

#     def __init__(self):
#         self.logger = logger
#         self.twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
#         self.twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
#         self.twilio_phone_number = os.getenv('TWILIO_PHONE_NUMBER')

#         if not all([self.twilio_account_sid, self.twilio_auth_token, self.twilio_phone_number]):
#             self.logger.warning(
#                 "Twilio credentials not configured - SMS service will be disabled")

#     async def send_sms(self, to_number: str, message: str, event_context: Optional[Dict] = None) -> Dict[str, Any]:
#         """
#         Send SMS message via Twilio.

#         Args:
#             to_number: Recipient phone number
#             message: Message content
#             event_context: Optional event context for logging

#         Returns:
#             Dictionary with result information
#         """
#         try:
#             if not self.twilio_account_sid:
#                 return {
#                     'success': False,
#                     'error': 'Twilio not configured',
#                     'message': 'SMS service not available'
#                 }

#             # Import Twilio client here to avoid dependency issues
#             from twilio.rest import Client

#             client = Client(self.twilio_account_sid, self.twilio_auth_token)

#             # Send message
#             message_obj = client.messages.create(
#                 body=message,
#                 from_=self.twilio_phone_number,
#                 to=to_number
#             )

#             self.logger.info(f"SMS sent successfully: {message_obj.sid}")

#             return {
#                 'success': True,
#                 'message_id': message_obj.sid,
#                 'status': message_obj.status,
#                 'to': to_number,
#                 'message': message
#             }

#         except Exception as e:
#             self.logger.error(f"Failed to send SMS to {to_number}: {e}")
#             return {
#                 'success': False,
#                 'error': str(e),
#                 'to': to_number,
#                 'message': message
#             }

#     def format_sms_message(self, action_description: str, event_context: Dict[str, Any]) -> str:
#         """
#         Format SMS message based on action and event context.

#         Args:
#             action_description: Description of the action
#             event_context: Event context information

#         Returns:
#             Formatted SMS message
#         """
#         event_title = event_context.get('title', 'Upcoming Event')
#         event_time = event_context.get('start_time', 'Unknown time')
#         event_location = event_context.get('location', 'No location specified')
#         event_description = event_context.get(
#             'description', 'No description available')

#         # Format the time if it's a datetime string
#         if isinstance(event_time, str) and 'T' in event_time:
#             try:
#                 dt = datetime.fromisoformat(event_time.replace('Z', '+00:00'))
#                 event_time = dt.strftime('%Y-%m-%d %H:%M')
#             except:
#                 pass

#         # Enhanced SMS formatting for all notification types
#         message = f"🔔 {action_description}\n\n"
#         message += f"Event: {event_title}\n"
#         message += f"Time: {event_time}\n"

#         if event_location and event_location != 'No location specified':
#             message += f"Location: {event_location}\n"

#         # Add description if available and not too long
#         if event_description and event_description != 'No description available':
#             # Truncate description if too long for SMS
#             if len(event_description) > 100:
#                 event_description = event_description[:97] + "..."
#             message += f"Details: {event_description}\n"

#         # Add action-specific information
#         if 'email' in action_description.lower():
#             message += "\n📧 Sent via SMS (email requested)"
#         elif 'reminder' in action_description.lower():
#             message += "\n⏰ Reminder set"
#         elif 'preparation' in action_description.lower():
#             message += "\n📋 Preparation needed"
#         elif 'document' in action_description.lower():
#             message += "\n📄 Document request"
#         elif 'research' in action_description.lower():
#             message += "\n🔍 Research task"

#         message += "\nSent by your AI Assistant"

#         return message


# class EmailService:
#     """
#     Email service for sending notifications.

#     This service can integrate with various email providers.
#     """

#     def __init__(self):
#         self.logger = logger
#         self.smtp_server = os.getenv('SMTP_SERVER')
#         self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
#         self.smtp_username = os.getenv('SMTP_USERNAME')
#         self.smtp_password = os.getenv('SMTP_PASSWORD')

#         if not all([self.smtp_server, self.smtp_username, self.smtp_password]):
#             self.logger.warning(
#                 "SMTP credentials not configured - Email service will be disabled")

#     async def send_email(self, to_email: str, subject: str, body: str, event_context: Optional[Dict] = None) -> Dict[str, Any]:
#         """
#         Send email message.

#         Args:
#             to_email: Recipient email address
#             subject: Email subject
#             body: Email body
#             event_context: Optional event context for logging

#         Returns:
#             Dictionary with result information
#         """
#         try:
#             if not self.smtp_server:
#                 return {
#                     'success': False,
#                     'error': 'SMTP not configured',
#                     'message': 'Email service not available'
#                 }

#             # Import email libraries here
#             import smtplib
#             from email.mime.multipart import MIMEMultipart
#             from email.mime.text import MIMEText

#             # Create message
#             msg = MIMEMultipart()
#             msg['From'] = self.smtp_username
#             msg['To'] = to_email
#             msg['Subject'] = subject

#             # Add body
#             msg.attach(MIMEText(body, 'html'))

#             # Send email
#             with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
#                 server.starttls()
#                 server.login(self.smtp_username, self.smtp_password)
#                 server.send_message(msg)

#             self.logger.info(f"Email sent successfully to {to_email}")

#             return {
#                 'success': True,
#                 'message_id': f"email_{datetime.utcnow().isoformat()}",
#                 'to': to_email,
#                 'subject': subject
#             }

#         except Exception as e:
#             self.logger.error(f"Failed to send email to {to_email}: {e}")
#             return {
#                 'success': False,
#                 'error': str(e),
#                 'to': to_email,
#                 'subject': subject
#             }

#     def format_email_message(self, action_description: str, event_context: Dict[str, Any]) -> tuple[str, str]:
#         """
#         Format email subject and body based on action and event context.

#         Args:
#             action_description: Description of the action
#             event_context: Event context information

#         Returns:
#             Tuple of (subject, body)
#         """
#         event_title = event_context.get('title', 'Upcoming Event')
#         event_time = event_context.get('start_time', 'Unknown time')
#         event_location = event_context.get('location', 'No location specified')
#         event_description = event_context.get(
#             'description', 'No description available')

#         # Format the time if it's a datetime string
#         if isinstance(event_time, str) and 'T' in event_time:
#             try:
#                 dt = datetime.fromisoformat(event_time.replace('Z', '+00:00'))
#                 event_time = dt.strftime('%Y-%m-%d %H:%M')
#             except:
#                 pass

#         subject = f"🔔 {action_description} - {event_title}"

#         body = f"""
#         <html>
#         <body>
#             <h2>{action_description}</h2>

#             <h3>Event Details:</h3>
#             <ul>
#                 <li><strong>Event:</strong> {event_title}</li>
#                 <li><strong>Time:</strong> {event_time}</li>
#                 <li><strong>Location:</strong> {event_location}</li>
#             </ul>

#             {f'<h3>Description:</h3><p>{event_description}</p>' if event_description != 'No description available' else ''}

#             <hr>
#             <p><em>Sent by your AI Assistant</em></p>
#         </body>
#         </html>
#         """

#         return subject, body


# class ReminderService:
#     """
#     Service for creating reminders and tasks.

#     This service can integrate with various reminder/task systems.
#     """

#     def __init__(self):
#         self.logger = logger

#     async def create_reminder(self, title: str, description: str, due_time: Optional[str] = None,
#                               event_context: Optional[Dict] = None) -> Dict[str, Any]:
#         """
#         Create a reminder or task.

#         Args:
#             title: Reminder title
#             description: Reminder description
#             due_time: Optional due time
#             event_context: Optional event context

#         Returns:
#             Dictionary with result information
#         """
#         try:
#             # For now, we'll just log the reminder creation
#             # In a real implementation, this would integrate with a task/reminder system

#             reminder_id = f"reminder_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

#             self.logger.info(f"Created reminder: {reminder_id} - {title}")

#             return {
#                 'success': True,
#                 'reminder_id': reminder_id,
#                 'title': title,
#                 'description': description,
#                 'due_time': due_time
#             }

#         except Exception as e:
#             self.logger.error(f"Failed to create reminder '{title}': {e}")
#             return {
#                 'success': False,
#                 'error': str(e),
#                 'title': title
#             }

#     def format_reminder_title(self, action_description: str, event_context: Dict[str, Any]) -> str:
#         """
#         Format reminder title based on action and event context.

#         Args:
#             action_description: Description of the action
#             event_context: Event context information

#         Returns:
#             Formatted reminder title
#         """
#         event_title = event_context.get('title', 'Upcoming Event')
#         return f"{action_description} - {event_title}"


# def create_sms_service() -> SMSService:
#     """
#     Factory function to create SMS service.

#     Returns:
#         SMSService instance
#     """
#     return SMSService()


# def create_email_service() -> EmailService:
#     """
#     Factory function to create email service.

#     Returns:
#         EmailService instance
#     """
#     return EmailService()


# def create_reminder_service() -> ReminderService:
#     """
#     Factory function to create reminder service.

#     Returns:
#         ReminderService instance
#     """
#     return ReminderService()
