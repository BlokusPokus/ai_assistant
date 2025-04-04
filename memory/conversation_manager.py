"""
Manages conversation state, IDs, and archival logic.
Uses the new database structure for persistence.
"""
from datetime import datetime, timedelta
import hashlib
from typing import Optional

from memory.memory_storage import store_summary
from memory.summary_engine import summarize_and_archive


def get_conversation_id(user_id: str, message: str) -> str:
    """
    Generate a unique conversation ID using SHA256 hash.
    This ensures consistent IDs for the same user+message combination.

    Args:
        user_id (str): Unique identifier for the user
        message (str): The message content

    Returns:
        str: SHA256 hash to use as conversation ID
    """
    # Combine user_id and message with a colon separator
    hash_input = f"{user_id}:{message}"
    # Generate SHA256 hash and return as hex string
    return hashlib.sha256(hash_input.encode()).hexdigest()


def should_resume_conversation(last_timestamp: Optional[datetime]) -> bool:
    """
    Determine if a conversation should be resumed based on its last activity.
    Uses a 30-minute window for conversation continuity.

    Logic:
    1. If no timestamp exists (new conversation) -> False
    2. If last activity was < 30 mins ago -> True
    3. If last activity was > 30 mins ago -> False

    Args:
        last_timestamp: When the conversation was last updated (from database)

    Returns:
        bool: True if conversation should be resumed
    """
    # Handle case where no previous conversation exists
    if not last_timestamp:
        return False

    # Define cutoff time (30 minutes ago)
    cutoff = datetime.utcnow() - timedelta(minutes=30)

    # Compare last activity to cutoff
    # If last_timestamp > cutoff, the conversation is recent enough to resume
    return last_timestamp > cutoff


async def archive_conversation(conversation_id: str, user_id: str) -> None:
    """
    Archive a conversation by generating and storing a summary.
    This is an async operation because it involves database access.

    Steps:
    1. Generate summary from conversation messages
    2. Store the summary for future context

    Args:
        conversation_id: ID of conversation to archive
        user_id: User the conversation belongs to
    """
    # Generate summary (async operation)
    summary = await summarize_and_archive(conversation_id)

    # Store the summary in the database (async operation)
    await store_summary(user_id, summary)
