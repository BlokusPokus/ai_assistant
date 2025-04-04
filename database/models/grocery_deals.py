from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Date
from .base import Base


class GroceryDeal(Base):
    __tablename__ = 'grocery_deals'

    id = Column(Integer, primary_key=True)
    source = Column(String)
    title = Column(String)
    price = Column(String)
    image_url = Column(String)
    flyer_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
