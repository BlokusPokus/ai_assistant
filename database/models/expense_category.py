from sqlalchemy import Column, Integer, String
from .base import Base


class ExpenseCategory(Base):
    __tablename__ = 'expense_categories'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
