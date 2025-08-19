from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String

from .base import Base


class Expense(Base):
    __tablename__ = 'expenses'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    amount = Column(Numeric(10, 2))
    category_id = Column(Integer, ForeignKey('expense_categories.id'))
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
