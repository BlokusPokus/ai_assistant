from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base import Base
from .users import User  # Import the User model


class MemoryChunk(Base):
    __tablename__ = 'memory_chunks'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    content = Column(String)
    embedding = Column(JSON)  # Changed from String to JSON
    created_at = Column(DateTime, default=datetime.utcnow)

    # Renamed from 'metadata' to 'meta_entries'
    meta_entries = relationship(
        "MemoryMetadata", back_populates="chunk", cascade="all, delete-orphan")
    # Use the imported User class directly
    user = relationship(User, back_populates="memory_chunks")
