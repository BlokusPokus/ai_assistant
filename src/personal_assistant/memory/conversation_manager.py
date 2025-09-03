"""
Manages conversation state, IDs, and archival logic.
Uses the new normalized database structure for persistence.
"""
import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import desc, select
from sqlalchemy.exc import SQLAlchemyError

from ..config.settings import settings
from ..database.crud.utils import add_record_no_commit
from ..database.session import AsyncSessionLocal

logger = logging.getLogger(__name__)


async def get_conversation_id(user_id: int) -> Optional[str]:
    """
    Retrieve the latest conversation_id for a user, or None if not found.

    This function queries the new normalized database schema for the most recent
    conversation associated with the given user.

    Args:
        user_id (int): The user ID to search for conversations

    Returns:
        Optional[str]: The conversation ID if found, None otherwise

    Example:
        >>> conv_id = await get_conversation_id(126)
        >>> if conv_id:
        ...     print(f"Found conversation: {conv_id}")
        ... else:
        ...     print("No conversation found")
    """
    # Input validation
    if user_id is None:
        logger.error("user_id cannot be None")
        return None

    try:
        # Use new normalized storage
        from ..database.models.conversation_state import ConversationState

        async with AsyncSessionLocal() as session:
            stmt = (
                select(ConversationState.conversation_id)
                .where(ConversationState.user_id == user_id)
                .order_by(desc(ConversationState.updated_at))
                .limit(1)
            )
            result = await session.execute(stmt)
            conversation_id = result.scalar_one_or_none()

            if conversation_id:
                logger.debug(
                    f"Found conversation ID in normalized storage: {conversation_id}"
                )
                return conversation_id
            else:
                logger.debug(f"No conversation found in normalized storage")
                return None
    except Exception as e:
        logger.error(f"Error getting conversation ID for user {user_id}: {e}")
        return None


async def create_new_conversation(user_id: int) -> Optional[str]:
    """
    Create a new conversation for a user and return the conversation ID.

    Args:
        user_id (int): The user ID for the new conversation

    Returns:
        Optional[str]: The new conversation ID (UUID string) or None if failed

    Raises:
        ValueError: If user_id is invalid
    """
    # Input validation
    if user_id is None:
        logger.error("user_id cannot be None")
        return None

    try:
        # Validate user exists (you'll need to implement this)
        # await validate_user_exists(user_id)

        conversation_id = str(uuid.uuid4())
        logger.info(f"Creating new conversation {conversation_id} for user {user_id}")

        async with AsyncSessionLocal() as session:
            async with session.begin():  # Start transaction
                try:
                    # Create entry in new normalized storage
                    from ..database.models.conversation_state import ConversationState

                    # Create entry in conversation_states table
                    conversation_state_data = {
                        "conversation_id": conversation_id,
                        "user_id": user_id,
                        "user_input": "",
                        "focus_areas": [],
                        "step_count": 0,
                        "last_tool_result": None,
                        "created_at": datetime.now(timezone.utc),
                        "updated_at": datetime.now(timezone.utc),
                    }
                    await add_record_no_commit(
                        session, ConversationState, conversation_state_data
                    )
                    logger.debug(
                        f"✅ Created conversation in normalized storage: {conversation_id}"
                    )

                    logger.info(f"Successfully created conversation {conversation_id}")
                    return conversation_id

                except SQLAlchemyError as e:
                    logger.error(f"Database error creating conversation: {e}")
                    raise  # This will trigger rollback

    except SQLAlchemyError as e:
        logger.error(f"Failed to create conversation for user {user_id}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error creating conversation for user {user_id}: {e}")
        return None


def should_resume_conversation(last_timestamp: Optional[datetime]) -> bool:
    """
    Determine if a conversation should be resumed based on its last activity.
    Uses a configurable window (default: 30 minutes) for conversation continuity.

    Logic:
    1. If no timestamp exists (new conversation) -> False
    2. If last activity was within the resume window -> True
    3. If last activity was outside the resume window -> False

    The resume window is configurable via CONVERSATION_RESUME_WINDOW_MINUTES setting.

    Args:
        last_timestamp: When the conversation was last updated (from database)

    Returns:
        bool: True if conversation should be resumed
    """
    # Handle case where no previous conversation exists
    if not last_timestamp:
        logger.debug("No timestamp provided, starting new conversation")
        return False

    # Database returns timezone-aware timestamps, so we need timezone-aware comparison
    # Define cutoff time (configurable minutes ago) - use timezone-aware UTC datetime
    cutoff = datetime.now(timezone.utc) - timedelta(
        minutes=settings.CONVERSATION_RESUME_WINDOW_MINUTES
    )

    # Compare last activity to cutoff
    # If last_timestamp > cutoff, the conversation is recent enough to resume
    should_resume = last_timestamp > cutoff

    logger.debug(
        f"Conversation resumption decision: "
        f"last_timestamp={last_timestamp}, "
        f"cutoff={cutoff}, "
        f"time_diff={datetime.now(timezone.utc) - last_timestamp}, "
        f"resume_window={settings.CONVERSATION_RESUME_WINDOW_MINUTES} minutes, "
        f"should_resume={should_resume}"
    )

    return should_resume
