from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from .base import Base


class GroceryItem(Base):
    __tablename__ = 'grocery_items'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String)
    quantity = Column(String)
    added_at = Column(DateTime, default=datetime.utcnow)
