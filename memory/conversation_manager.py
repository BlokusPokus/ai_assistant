from datetime import datetime, timedelta, timezone
import hashlib

from memory.memory_storage import store_summary
from memory.summary_engine import summarize_and_archive
"""
Handles conversation ID generation and expiration logic.
"""

CONVERSATION_TTL_MINUTES = 30


def get_conversation_id(user_id: str, input_text: str) -> str:
    """
    Generate or retrieve the appropriate conversation ID.

    Args:
        user_id (str): ID of the user
        input_text (str): Current input message

    Returns:
        str: Conversation ID
    """
    hash_input = f"{user_id}-{input_text[:50]}"
    return hashlib.sha256(hash_input.encode()).hexdigest()


def should_resume_conversation(timestamp: datetime) -> bool:
    """
    Decide whether a conversation should be resumed or reset.

    Args:
        conversation_id (str): Conversation ID
        timestamp (datetime): Time of last interaction

    Returns:
        bool: True if still valid, False if expired
    """
    if timestamp is None:
        return False
    return (datetime.now(timezone.utc) - timestamp) < timedelta(minutes=CONVERSATION_TTL_MINUTES)


def expire_conversation(conversation_id: str) -> None:
    """
    Expire a conversation and trigger summarization if needed.

    Args:
        conversation_id (str): ID to expire
    """
    try:
        summary = summarize_and_archive(conversation_id)
        store_summary(conversation_id, summary)
        print(
            f"[ConversationManager] Expired and summarized conversation {conversation_id}")
    except Exception as e:
        print(f"[ConversationManager] Error during expiration: {e}")
