from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .base import Base
from .users import User  # Import the User model


class MemoryChunk(Base):
    __tablename__ = 'memory_chunks'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    # Changed from String to Text to allow larger content
    content = Column(Text)
    embedding = Column(JSON)  # Changed from String to JSON
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Renamed from 'metadata' to 'meta_entries'
    meta_entries = relationship(
        "MemoryMetadata", back_populates="chunk", cascade="all, delete-orphan")
    # Use the imported User class directly
    user = relationship(User, back_populates="memory_chunks")
