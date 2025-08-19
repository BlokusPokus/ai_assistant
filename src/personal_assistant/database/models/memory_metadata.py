from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .base import Base


class MemoryMetadata(Base):
    __tablename__ = 'memory_metadata'

    id = Column(Integer, primary_key=True)
    chunk_id = Column(Integer, ForeignKey('memory_chunks.id'))
    key = Column(String)
    value = Column(String)

    # Other side of the relationship
    chunk = relationship("MemoryChunk", back_populates="meta_entries")
