import logging

from memory.client import MemoryDBClient

# ... existing imports ...

logger = logging.getLogger(__name__)


class MockMemoryDBClient(MemoryDBClient):
    """Simple in-memory implementation for testing without vectors"""

    def __init__(self):
        self.records = []
        logger.info("Initialized MockMemoryDBClient")

    def add_record(self, user_id: int, content: str, metadata: dict):
        """Add a record to the in-memory database."""
        self.records.append({
            "user_id": user_id,
            "content": content,
            "metadata": metadata
        })
        logger.info(
            "Added in-memory record for user_id: %d with content: %s", user_id, content)

    def query_records(self, user_id: int, query: str, n_results: int):
        """Query the in-memory database for similar records."""
        results = [
            record for record in self.records
            if record["user_id"] == user_id and query.lower() in record["content"].lower()
        ]
        logger.info("Queried in-memory records for user_id: %d with query: '%s', found: %d results",
                    user_id, query, len(results))
        return results[:n_results]
