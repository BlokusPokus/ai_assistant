from datetime import datetime, timezone
from typing import Optional, List
import json

from memory.client import MemoryRecord

# Simulated in-memory DB for the purpose of demonstration
db = {
    "conversation_state": {},  # conversation_id -> {"state": ..., "last_updated": ...}
    # user_id -> [{"topic": ..., "summary": ..., "timestamp": ...}]
    "summaries": {},
    "ltm": []                  # list of long-term memory entries
}


def load_state(self, conversation_id: str) -> dict:
    """
    Load the state from the database using the conversation_id.

    Args:
        conversation_id (str): The ID of the conversation.

    Returns:
        dict: The agent state or an empty dictionary if not found.
    """
    # Step 2: Query the database for records with the given conversation_id
    session = self.client.Session()
    results = session.query(MemoryRecord).filter(
        MemoryRecord.meta_data['conversation_id'].astext == conversation_id
    ).all()
    session.close()

    # Step 3: Deserialize the results into a state
    if results:
        # Assuming the first result contains the necessary state
        state_data = results[0].meta_data
        return state_data
    else:
        # Return an empty dictionary if no records are found
        return {}


def save_state(self, conversation_id: str, state: dict) -> None:
    """
    Save short-term memory state and update timestamp.

    Args:
        conversation_id (str): The ID of the conversation.
        state (dict): The state to be saved.

    Returns:
        None
    """
    # Step 2: Update the database with the new state
    session = self.client.Session()
    existing_record = session.query(MemoryRecord).filter(
        MemoryRecord.meta_data['conversation_id'].astext == conversation_id
    ).first()

    if existing_record:
        # Update existing record
        existing_record.meta_data = state
        existing_record.meta_data['last_updated'] = datetime.now(timezone.utc)
    else:
        # Create a new record if it doesn't exist
        new_record = MemoryRecord(
            meta_data={
                'conversation_id': conversation_id,
                **state,
                'last_updated': datetime.now(timezone.utc)
            }
        )
        session.add(new_record)

    session.commit()
    session.close()


def get_conversation_timestamp(self, conversation_id: str) -> Optional[datetime]:
    """
    Retrieve the last updated timestamp for a conversation.

    Args:
        conversation_id (str): The ID of the conversation.

    Returns:
        Optional[datetime]: The last updated timestamp or None if not found.
    """
    session = self.client.Session()
    record = session.query(MemoryRecord).filter(
        MemoryRecord.meta_data['conversation_id'].astext == conversation_id
    ).first()
    session.close()

    if record:
        return record.meta_data.get('last_updated')
    return None


def store_summary(self, conversation_id: str, summary: str) -> None:
    """
    Store a fallback summary for a given conversation.

    Args:
        conversation_id (str): The ID of the conversation.
        summary (str): The summary to be stored.

    Returns:
        None
    """
    session = self.client.Session()
    # Assuming you have a way to map conversation_id to user_id
    user_id = self.get_user_id_from_conversation(conversation_id)

    # Create a new record for the summary
    summary_record = MemoryRecord(
        user_id=user_id,
        content=summary,
        meta_data={
            'conversation_id': conversation_id,
            'timestamp': datetime.now(timezone.utc)
        }
    )
    session.add(summary_record)
    session.commit()
    session.close()


def load_latest_summary(self, user_id: str, topic: Optional[str] = None) -> str:
    """
    Load the latest summary for a given user/topic.

    Args:
        user_id (str): The ID of the user.
        topic (Optional[str]): The topic to filter summaries.

    Returns:
        str: The latest summary text or an empty string if not found.
    """
    session = self.client.Session()
    query = session.query(MemoryRecord).filter(
        MemoryRecord.user_id == user_id
    )

    if topic:
        query = query.filter(MemoryRecord.meta_data['topic'].astext == topic)

    # Order by timestamp descending to get the latest summary
    summary_record = query.order_by(
        MemoryRecord.meta_data['timestamp'].desc()
    ).first()

    session.close()

    if summary_record:
        return summary_record.content
    return ""


def add_ltm_entry(self, entry: dict) -> None:
    """
    Add a structured long-term memory entry.

    Args:
        entry (dict): The entry to be added.

    Returns:
        None
    """
    entry["timestamp"] = datetime.now(timezone.utc)

    session = self.client.Session()
    ltm_record = MemoryRecord(
        user_id=entry.get("user_id"),
        content=entry.get("content"),
        meta_data=entry
    )
    session.add(ltm_record)
    session.commit()
    session.close()


def query_ltm(self, user_id: str, topic: Optional[str] = None, tags: Optional[List[str]] = None) -> List[dict]:
    """
    Query long-term memory for relevant entries.

    Args:
        user_id (str): The ID of the user.
        topic (Optional[str]): The topic to filter entries.
        tags (Optional[List[str]]): The tags to filter entries.

    Returns:
        List[dict]: A list of matching LTM entries.
    """
    session = self.client.Session()
    query = session.query(MemoryRecord).filter(
        MemoryRecord.user_id == user_id
    )

    if topic:
        query = query.filter(MemoryRecord.meta_data['topic'].astext == topic)

    if tags:
        query = query.filter(
            MemoryRecord.meta_data['tags'].astext.contains(tags)
        )

    results = query.all()
    session.close()

    return [record.meta_data for record in results]


# def save_conversation_state(conversation_id: str, state: dict) -> None:
#     """Save the conversation state in memory."""
#     # Implementation for in-memory storage
#     pass


# def load_conversation_state(conversation_id: str) -> dict:
#     """Load the conversation state from memory."""
#     # Implementation for in-memory retrieval
#     pass
