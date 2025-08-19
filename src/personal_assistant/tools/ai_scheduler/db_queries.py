import logging
from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ...database.models.event_processing_log import EventProcessingLog
from ...database.models.events import Event
from ...database.models.session import AsyncSessionLocal

logger = logging.getLogger(__name__)


async def get_upcoming_events(hours_ahead: int = 2) -> List[Event]:
    """
    Query database for upcoming events in the next N hours.

    Args:
        hours_ahead: Number of hours to look ahead (default: 2)

    Returns:
        List of Event objects that need processing
    """
    try:
        async with AsyncSessionLocal() as session:
            # Calculate time window
            now = datetime.utcnow()
            future_time = now + timedelta(hours=hours_ahead)

            # Query for events that:
            # 1. Start within the next N hours
            # 2. Have processing_status = 'pending'
            # 3. Haven't been handled yet
            query = select(Event).where(
                Event.start_time >= now,
                Event.start_time <= future_time,
                Event.processing_status == 'pending'
            ).order_by(Event.start_time.asc())

            result = await session.execute(query)
            events = result.scalars().all()

            logger.info(f"Found {len(events)} upcoming events to process")
            return events

    except Exception as e:
        logger.error(f"Error querying upcoming events: {e}")
        return []


async def mark_event_processing(event_id: int) -> bool:
    """
    Mark an event as being processed.

    Args:
        event_id: ID of the event to mark

    Returns:
        True if successful, False otherwise
    """
    try:
        async with AsyncSessionLocal() as session:
            # Update event status
            update_query = update(Event).where(
                Event.id == event_id
            ).values(
                processing_status='processing',
                last_checked=datetime.utcnow()
            )

            result = await session.execute(update_query)
            await session.commit()

            # Log the processing attempt
            log_entry = EventProcessingLog(
                event_id=event_id,
                processed_at=datetime.utcnow(),
                processing_status='processing'
            )

            session.add(log_entry)
            await session.commit()

            logger.info(f"Marked event {event_id} as processing")
            return True

    except Exception as e:
        logger.error(f"Error marking event {event_id} as processing: {e}")
        return False


async def mark_event_completed(event_id: int, agent_response: str = None) -> bool:
    """
    Mark an event as completed processing.

    Args:
        event_id: ID of the event to mark
        agent_response: Optional response from the agent

    Returns:
        True if successful, False otherwise
    """
    try:
        async with AsyncSessionLocal() as session:
            # Update event status
            update_query = update(Event).where(
                Event.id == event_id
            ).values(
                processing_status='completed',
                handled_at=datetime.utcnow(),
                agent_response=agent_response,
                last_checked=datetime.utcnow()
            )

            result = await session.execute(update_query)
            await session.commit()

            # Log the completion
            log_entry = EventProcessingLog(
                event_id=event_id,
                processed_at=datetime.utcnow(),
                processing_status='completed',
                agent_response=agent_response
            )

            session.add(log_entry)
            await session.commit()

            logger.info(f"Marked event {event_id} as completed")
            return True

    except Exception as e:
        logger.error(f"Error marking event {event_id} as completed: {e}")
        return False


async def mark_event_failed(event_id: int, error_message: str) -> bool:
    """
    Mark an event as failed processing.

    Args:
        event_id: ID of the event to mark
        error_message: Error message describing the failure

    Returns:
        True if successful, False otherwise
    """
    try:
        async with AsyncSessionLocal() as session:
            # Update event status
            update_query = update(Event).where(
                Event.id == event_id
            ).values(
                processing_status='failed',
                last_checked=datetime.utcnow()
            )

            result = await session.execute(update_query)
            await session.commit()

            # Log the failure
            log_entry = EventProcessingLog(
                event_id=event_id,
                processed_at=datetime.utcnow(),
                processing_status='failed',
                error_message=error_message
            )

            session.add(log_entry)
            await session.commit()

            logger.error(f"Marked event {event_id} as failed: {error_message}")
            return True

    except Exception as e:
        logger.error(f"Error marking event {event_id} as failed: {e}")
        return False


async def reset_failed_events() -> int:
    """
    Reset events that have been in 'failed' status for more than 1 hour.
    This allows retry of failed events.

    Returns:
        Number of events reset
    """
    try:
        async with AsyncSessionLocal() as session:
            # Find events that failed more than 1 hour ago
            cutoff_time = datetime.utcnow() - timedelta(hours=1)

            update_query = update(Event).where(
                Event.processing_status == 'failed',
                Event.last_checked < cutoff_time
            ).values(
                processing_status='pending',
                last_checked=None
            )

            result = await session.execute(update_query)
            await session.commit()

            reset_count = result.rowcount
            logger.info(f"Reset {reset_count} failed events to pending status")
            return reset_count

    except Exception as e:
        logger.error(f"Error resetting failed events: {e}")
        return 0


async def get_event_by_id(event_id: int) -> Optional[Event]:
    """
    Get a specific event by ID.

    Args:
        event_id: ID of the event to retrieve

    Returns:
        Event object or None if not found
    """
    try:
        async with AsyncSessionLocal() as session:
            query = select(Event).where(Event.id == event_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    except Exception as e:
        logger.error(f"Error retrieving event {event_id}: {e}")
        return None


async def cleanup_old_processing_logs(days_to_keep: int = 30) -> int:
    """
    Clean up old processing logs that are older than the specified number of days.

    Args:
        days_to_keep: Number of days of logs to keep (default: 30)

    Returns:
        Number of log entries deleted
    """
    try:
        async with AsyncSessionLocal() as session:
            # Calculate cutoff date
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)

            # Delete old processing logs
            delete_query = delete(EventProcessingLog).where(
                EventProcessingLog.processed_at < cutoff_date
            )

            result = await session.execute(delete_query)
            await session.commit()

            deleted_count = result.rowcount
            logger.info(
                f"Cleaned up {deleted_count} old processing logs (older than {days_to_keep} days)")
            return deleted_count

    except Exception as e:
        logger.error(f"Error cleaning up old processing logs: {e}")
        return 0
