"""
Vector database client interfaces and implementations.
"""
import logging
from typing import List, Dict, Any
import numpy as np
from agent_core.memory.interface import MemoryInterface
from sqlalchemy import create_engine, Column, Integer, String, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()


class MemoryRecord(Base):
    __tablename__ = 'memory_records'
    id = Column(Integer, primary_key=True)
    vector = Column(JSON)  # Store vector as JSON
    document = Column(String)
    meta_data = Column(JSON)  # Renamed from 'metadata' to 'meta_data'
    user_id = Column(Integer)
    content = Column(String)


class MemoryDBClient:
    """Base interface for memory database clients"""

    def __init__(self, db_url: str):
        """Initialize the SQLAlchemy engine and session."""
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        logger.info("Initialized MemoryDBClient with database URL: %s", db_url)

    def embed_text(self, text: str) -> np.ndarray:
        """Convert text to vector embeddings."""
        # Use your embedding model here
        # Example using a hypothetical embedding model
        embedding = self.embedding_model.embed_text(text)
        logger.debug("Embedded text: %s", text)
        return np.array(embedding)

    def add_record(self, user_id: int, content: str, metadata: dict):
        """Add a record to the database."""
        session = self.Session()
        memory_record = MemoryRecord(
            user_id=user_id,
            content=content,
            meta_data=metadata
        )
        session.add(memory_record)
        session.commit()
        session.close()
        logger.info("Added record for user_id: %d with content: %s",
                    user_id, content)

    def query_records(self, user_id: int, query: str, n_results: int):
        """Query the database for similar records."""
        session = self.Session()
        # Implement a simple text search logic
        results = session.query(MemoryRecord).filter(
            MemoryRecord.user_id == user_id,
            MemoryRecord.content.ilike(f"%{query}%")
        ).limit(n_results).all()
        session.close()
        logger.info("Queried records for user_id: %d with query: '%s', found: %d results",
                    user_id, query, len(results))
        return results


class Collection:
    """Base interface for vector collections"""

    def query(self, query_embeddings: np.ndarray, n_results: int) -> List[Dict[str, Any]]:
        """Search for similar vectors"""
        raise NotImplementedError

    def add(self, embeddings: List[np.ndarray], documents: List[str], metadatas: List[Dict]):
        """Add vectors to collection"""
        raise NotImplementedError


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


class VectorMemory(MemoryInterface):
    def __init__(self, client: MemoryDBClient):
        self.client = client

    def add(self, content: str, metadata: dict):
        """Add content to the memory database."""
        vector = self.client.embed_text(content)
        self.client.add_record(vector, content, metadata)

    def query(self, query: str, k: int):
        """Query the memory database."""
        query_vector = self.client.embed_text(query)
        return self.client.query_records(query_vector, n_results=k)
