from datetime import datetime
from sqlalchemy import Column, Integer, JSON, DateTime, ForeignKey
from .base import Base


class GroceryAnalysis(Base):
    __tablename__ = 'grocery_analysis'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    analysis = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
