from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, JSON

from .base import Base


class GroceryDeal(Base):
    __tablename__ = "grocery_deals"

    # IGA product ID (primary key)
    id = Column(Integer, primary_key=True)
    
    # Product information
    name = Column(String(255), nullable=False)
    sku = Column(String(100), nullable=False)
    description = Column(Text)
    brand = Column(String(255))
    
    # Deal validity
    valid_from = Column(DateTime, nullable=False)
    valid_to = Column(DateTime, nullable=False)
    
    # Pricing information
    price_text = Column(String(100), nullable=False)  # e.g., "2.99"
    post_price_text = Column(String(255))  # e.g., "/lb $6.59/kg Member price"
    original_price = Column(Float)  # Original price if on sale
    
    # Categories and metadata
    categories = Column(JSON)  # JSON array of categories
    web_commission_url = Column(Text)  # Product URL
    
    # Timestamps
    scraped_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
