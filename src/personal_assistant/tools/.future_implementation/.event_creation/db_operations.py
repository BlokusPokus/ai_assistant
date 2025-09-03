import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...database.models.event_creation_logs import EventCreationLog
from ...database.models.events import Event
from ...database.models.recurrence_patterns import RecurrencePattern

logger = logging.getLogger(__name__)


class EventDatabaseOperations:
    """Database operations for event creation and management."""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_event_by_id(self, event_id: int) -> Optional[Event]:
        """Get event by ID."""
        try:
            result = await self.db_session.execute(
                select(Event).where(Event.id == event_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting event by ID {event_id}: {e}")
            return None

    async def get_events_by_user(self, user_id: int, limit: int = 50) -> List[Event]:
        """Get events for a user."""
        try:
            result = await self.db_session.execute(
                select(Event)
                .where(Event.user_id == user_id)
                .order_by(Event.start_time.desc())
                .limit(limit)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting events for user {user_id}: {e}")
            return []

    async def get_upcoming_events(
        self, user_id: int, hours_ahead: int = 24
    ) -> List[Event]:
        """Get upcoming events for a user."""
        try:
            now = datetime.now()
            end_time = now + timedelta(hours=hours_ahead)

            result = await self.db_session.execute(
                select(Event)
                .where(
                    and_(
                        Event.user_id == user_id,
                        Event.start_time >= now,
                        Event.start_time <= end_time,
                    )
                )
                .order_by(Event.start_time.asc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting upcoming events for user {user_id}: {e}")
            return []

    async def get_recurring_events(self, user_id: int) -> List[Event]:
        """Get recurring events for a user."""
        try:
            result = await self.db_session.execute(
                select(Event)
                .where(and_(Event.user_id == user_id, Event.is_recurring == True))
                .order_by(Event.start_time.asc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting recurring events for user {user_id}: {e}")
            return []

    async def get_event_instances(self, parent_event_id: int) -> List[Event]:
        """Get all instances of a recurring event."""
        try:
            result = await self.db_session.execute(
                select(Event)
                .where(Event.parent_event_id == parent_event_id)
                .order_by(Event.start_time.asc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(
                f"Error getting event instances for parent {parent_event_id}: {e}"
            )
            return []

    async def delete_event(self, event_id: int, user_id: int) -> bool:
        """Delete an event."""
        try:
            event = await self.get_event_by_id(event_id)
            if not event or event.user_id != user_id:
                return False

            # If it's a recurring event, delete all instances
            if event.is_recurring and event.parent_event_id is None:
                # This is the parent event, delete all instances
                instances = await self.get_event_instances(event.id)
                for instance in instances:
                    await self.db_session.delete(instance)

                # Delete the recurrence pattern
                if event.recurrence_pattern_id:
                    pattern = await self.db_session.get(
                        RecurrencePattern, event.recurrence_pattern_id
                    )
                    if pattern:
                        await self.db_session.delete(pattern)

            await self.db_session.delete(event)
            await self.db_session.commit()
            return True

        except Exception as e:
            logger.error(f"Error deleting event {event_id}: {e}")
            await self.db_session.rollback()
            return False

    async def update_event(
        self, event_id: int, user_id: int, updates: Dict[str, Any]
    ) -> bool:
        """Update an event."""
        try:
            event = await self.get_event_by_id(event_id)
            if not event or event.user_id != user_id:
                return False

            # Update allowed fields
            allowed_fields = ["title", "description", "start_time", "end_time"]
            for field, value in updates.items():
                if field in allowed_fields and hasattr(event, field):
                    setattr(event, field, value)

            await self.db_session.commit()
            return True

        except Exception as e:
            logger.error(f"Error updating event {event_id}: {e}")
            await self.db_session.rollback()
            return False

    async def search_events(self, user_id: int, query: str) -> List[Event]:
        """Search events by title or description."""
        try:
            search_term = f"%{query}%"
            result = await self.db_session.execute(
                select(Event)
                .where(
                    and_(
                        Event.user_id == user_id,
                        or_(
                            Event.title.ilike(search_term),
                            Event.description.ilike(search_term),
                        ),
                    )
                )
                .order_by(Event.start_time.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error searching events for user {user_id}: {e}")
            return []

    async def get_creation_logs(
        self, user_id: int, limit: int = 20
    ) -> List[EventCreationLog]:
        """Get event creation logs for a user."""
        try:
            result = await self.db_session.execute(
                select(EventCreationLog)
                .where(EventCreationLog.user_id == user_id)
                .order_by(EventCreationLog.created_at.desc())
                .limit(limit)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting creation logs for user {user_id}: {e}")
            return []

    async def check_event_conflicts(
        self,
        user_id: int,
        start_time: datetime,
        end_time: datetime,
        exclude_event_id: Optional[int] = None,
    ) -> List[Event]:
        """Check for conflicting events."""
        try:
            query = select(Event).where(
                and_(
                    Event.user_id == user_id,
                    Event.start_time < end_time,
                    Event.end_time > start_time,
                )
            )

            if exclude_event_id:
                query = query.where(Event.id != exclude_event_id)

            result = await self.db_session.execute(query)
            return result.scalars().all()

        except Exception as e:
            logger.error(f"Error checking event conflicts for user {user_id}: {e}")
            return []

    async def get_event_statistics(self, user_id: int) -> Dict[str, Any]:
        """Get event statistics for a user."""
        try:
            # Get total events
            total_result = await self.db_session.execute(
                select(Event).where(Event.user_id == user_id)
            )
            total_events = len(total_result.scalars().all())

            # Get recurring events
            recurring_result = await self.db_session.execute(
                select(Event).where(
                    and_(Event.user_id == user_id, Event.is_recurring == True)
                )
            )
            recurring_events = len(recurring_result.scalars().all())

            # Get upcoming events
            # 1 week
            upcoming_events = await self.get_upcoming_events(user_id, hours_ahead=168)
            upcoming_count = len(upcoming_events)

            return {
                "total_events": total_events,
                "recurring_events": recurring_events,
                "upcoming_events": upcoming_count,
                "one_time_events": total_events - recurring_events,
            }

        except Exception as e:
            logger.error(f"Error getting event statistics for user {user_id}: {e}")
            return {
                "total_events": 0,
                "recurring_events": 0,
                "upcoming_events": 0,
                "one_time_events": 0,
            }
