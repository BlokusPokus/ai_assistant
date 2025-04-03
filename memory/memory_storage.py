from datetime import datetime, timezone
from typing import Optional, List
import json

# Simulated in-memory DB for the purpose of demonstration
db = {
    "conversation_state": {},  # conversation_id -> {"state": ..., "last_updated": ...}
    # user_id -> [{"topic": ..., "summary": ..., "timestamp": ...}]
    "summaries": {},
    "ltm": []                  # list of long-term memory entries
}


def load_state(conversation_id: str) -> dict:
    """
    Load short-term memory state.
    """
    record = db["conversation_state"].get(conversation_id)
    return record["state"] if record else {}


def save_state(conversation_id: str, state: dict) -> None:
    """
    Save short-term memory state and update timestamp.
    """
    db["conversation_state"][conversation_id] = {
        "state": state,
        "last_updated": datetime.now(timezone.utc)
    }


def get_conversation_timestamp(conversation_id: str) -> Optional[datetime]:
    """
    Retrieve the last updated timestamp for a conversation.
    """
    record = db["conversation_state"].get(conversation_id)
    return record["last_updated"] if record else None


def store_summary(conversation_id: str, summary: str) -> None:
    """
    Store a fallback summary for a given conversation.
    """
    # Here we assume you can map user_id from conversation_id in real logic
    user_id = "mock_user"  # Replace with real mapping
    db["summaries"].setdefault(user_id, []).append({
        "conversation_id": conversation_id,
        "summary": summary,
        "timestamp": datetime.now(timezone.utc)
    })


def load_latest_summary(user_id: str, topic: Optional[str] = None) -> str:
    """
    Load latest summary for a given user/topic.
    """
    summaries = db["summaries"].get(user_id, [])
    if topic:
        summaries = [s for s in summaries if topic in s.get("topic", "")]
    if summaries:
        summaries.sort(key=lambda x: x["timestamp"], reverse=True)
        return summaries[0]["summary"]
    return ""


def add_ltm_entry(entry: dict) -> None:
    """
    Add a structured long-term memory entry.
    """
    entry["timestamp"] = datetime.now(timezone.utc)
    db["ltm"].append(entry)


def query_ltm(user_id: str, topic: Optional[str] = None, tags: Optional[List[str]] = None) -> List[dict]:
    """
    Query long-term memory for relevant entries.
    """
    results = [e for e in db["ltm"] if e["user_id"] == user_id]
    if topic:
        results = [e for e in results if e.get("topic") == topic]
    if tags:
        results = [e for e in results if set(
            tags).intersection(set(e.get("tags", [])))]
    return results
