import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...database.models.event_creation_logs import EventCreationLog
from ...database.models.events import Event
from ...database.models.recurrence_patterns import (
    RecurrencePattern as DBRecurrencePattern,
)
from ...llm.llm_client import LLMClient
from .ai_parser import EventAIParser
from .event_details import EventDetails, RecurrencePattern, ValidationResult

logger = logging.getLogger(__name__)


class EventCreationTool:
    """Tool for creating events with recurring support."""

    def __init__(self, llm_client: LLMClient, db_session: AsyncSession):
        self.llm_client = llm_client
        self.db_session = db_session
        self.ai_parser = EventAIParser(llm_client)

    async def create_event(self, user_input: str, user_id: int) -> Dict[str, Any]:
        """Create event from natural language input."""
        try:
            # Log the creation attempt
            creation_log = EventCreationLog(
                user_id=user_id, user_input=user_input, created_events=0
            )

            # Parse event details using AI
            event_details = await self.ai_parser.parse_event_details(user_input)

            # Validate event details
            validation_result = await self.ai_parser.validate_event_details(
                event_details
            )

            if not validation_result.is_valid:
                creation_log.errors = "; ".join(validation_result.errors)
                await self._save_creation_log(creation_log)
                return {
                    "success": False,
                    "error": f"Invalid event details: {'; '.join(validation_result.errors)}",
                }

            # Create the base event
            base_event = await self._create_base_event(event_details, user_id)

            created_events = [base_event]

            # Handle recurring events
            if event_details.recurrence_pattern:
                recurring_events = await self._create_recurring_events(
                    base_event, event_details.recurrence_pattern
                )
                created_events.extend(recurring_events)

            # Update creation log
            creation_log.parsed_details = event_details.to_dict()
            creation_log.created_events = len(created_events)
            await self._save_creation_log(creation_log)

            # Format response
            response_details = self._format_response_details(
                event_details, len(created_events)
            )

            return {
                "success": True,
                "event_title": event_details.title,
                "details": response_details,
                "created_events": len(created_events),
                "event_ids": [event.id for event in created_events],
            }

        except Exception as e:
            logger.error(f"Error creating event: {e}")
            creation_log.errors = str(e)
            await self._save_creation_log(creation_log)
            return {"success": False, "error": f"Failed to create event: {str(e)}"}

    async def _create_base_event(
        self, event_details: EventDetails, user_id: int
    ) -> Event:
        """Create the base event in the database."""
        # Calculate end time
        end_time = event_details.start_time + timedelta(minutes=event_details.duration)

        # Create event object
        event = Event(
            user_id=user_id,
            title=event_details.title,
            description=event_details.description,
            start_time=event_details.start_time,
            end_time=end_time,
            source="sms_creation",
            is_recurring=bool(event_details.recurrence_pattern),
        )

        # Save to database
        self.db_session.add(event)
        await self.db_session.flush()  # Get the ID
        await self.db_session.commit()

        return event

    async def _create_recurring_events(
        self, base_event: Event, recurrence_pattern: Dict[str, Any]
    ) -> List[Event]:
        """Create recurring event instances."""
        try:
            # Create recurrence pattern in database
            db_pattern = DBRecurrencePattern(
                frequency=recurrence_pattern["frequency"],
                interval=recurrence_pattern.get("interval", 1),
                weekdays=recurrence_pattern.get("weekdays"),
                end_date=datetime.fromisoformat(recurrence_pattern["end_date"])
                if recurrence_pattern.get("end_date")
                else None,
                max_occurrences=recurrence_pattern.get("max_occurrences"),
            )

            self.db_session.add(db_pattern)
            await self.db_session.flush()  # Get the ID

            # Update base event with recurrence pattern
            base_event.recurrence_pattern_id = db_pattern.id
            base_event.is_recurring = True

            # Generate recurring instances
            instances = self._generate_recurring_instances(base_event, db_pattern)

            # Create instance events
            created_events = []
            for i, instance_datetime in enumerate(instances):
                instance_event = Event(
                    user_id=base_event.user_id,
                    title=base_event.title,
                    description=base_event.description,
                    start_time=instance_datetime,
                    end_time=instance_datetime
                    + timedelta(
                        minutes=(
                            base_event.end_time - base_event.start_time
                        ).total_seconds()
                        / 60
                    ),
                    source="sms_creation",
                    is_recurring=True,
                    parent_event_id=base_event.id,
                    recurrence_instance_number=i + 1,
                )

                self.db_session.add(instance_event)
                created_events.append(instance_event)

            await self.db_session.commit()
            return created_events

        except Exception as e:
            logger.error(f"Error creating recurring events: {e}")
            await self.db_session.rollback()
            raise

    def _generate_recurring_instances(
        self,
        base_event: Event,
        pattern: DBRecurrencePattern,
        max_instances: int = 52,  # Default to 1 year for weekly events
    ) -> List[datetime]:
        """Generate recurring event instances."""
        instances = []
        current_date = base_event.start_time

        # Set maximum occurrences based on frequency
        if pattern.frequency == "daily":
            max_instances = 365  # 1 year
        elif pattern.frequency == "weekly":
            max_instances = 52  # 1 year
        elif pattern.frequency == "monthly":
            max_instances = 12  # 1 year
        elif pattern.frequency == "yearly":
            max_instances = 10  # 10 years

        # Override with pattern max_occurrences if specified
        if pattern.max_occurrences:
            max_instances = min(max_instances, pattern.max_occurrences)

        for i in range(max_instances):
            if pattern.end_date and current_date > pattern.end_date:
                break

            instances.append(current_date)

            # Calculate next occurrence
            if pattern.frequency == "daily":
                current_date += timedelta(days=pattern.interval)
            elif pattern.frequency == "weekly":
                current_date += timedelta(weeks=pattern.interval)
            elif pattern.frequency == "monthly":
                # Simple monthly increment (not perfect for varying month lengths)
                year = current_date.year + (
                    (current_date.month - 1 + pattern.interval) // 12
                )
                month = ((current_date.month - 1 + pattern.interval) % 12) + 1
                current_date = current_date.replace(year=year, month=month)
            elif pattern.frequency == "yearly":
                current_date = current_date.replace(
                    year=current_date.year + pattern.interval
                )

        return instances

    async def _save_creation_log(self, creation_log: EventCreationLog):
        """Save event creation log to database."""
        try:
            self.db_session.add(creation_log)
            await self.db_session.commit()
        except Exception as e:
            logger.error(f"Error saving creation log: {e}")
            await self.db_session.rollback()

    def _format_response_details(
        self, event_details: EventDetails, num_events: int
    ) -> str:
        """Format response details for user."""
        details = []

        # Add title
        details.append(f"📅 {event_details.title}")

        # Add time
        time_str = event_details.start_time.strftime("%A, %B %d at %I:%M %p")
        details.append(f"⏰ {time_str}")

        # Add duration
        if event_details.duration != 60:  # Only show if not default
            hours = event_details.duration // 60
            minutes = event_details.duration % 60
            if hours > 0:
                duration_str = f"{hours}h {minutes}m" if minutes > 0 else f"{hours}h"
            else:
                duration_str = f"{minutes}m"
            details.append(f"⏱️ Duration: {duration_str}")

        # Add location if specified
        if event_details.location:
            details.append(f"📍 {event_details.location}")

        # Add recurrence info
        if event_details.recurrence_pattern:
            frequency = event_details.recurrence_pattern["frequency"]
            interval = event_details.recurrence_pattern.get("interval", 1)

            if interval == 1:
                recurrence_str = f"🔄 Recurring {frequency}"
            else:
                recurrence_str = f"🔄 Recurring every {interval} {frequency}"

            details.append(recurrence_str)
            details.append(f"📊 Created {num_events} instances")

        return "\n".join(details)
