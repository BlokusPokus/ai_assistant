from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from .base import Base


class BudgetSyncLog(Base):
    __tablename__ = "budget_sync_log"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    synced_at = Column(DateTime, default=datetime.utcnow)
    sync_status = Column(String)
