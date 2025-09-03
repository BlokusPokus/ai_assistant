from datetime import datetime

from sqlalchemy import ARRAY, Column, DateTime, Integer, String

from .base import Base


class RecurrencePattern(Base):
    __tablename__ = "recurrence_patterns"

    id = Column(Integer, primary_key=True)
    # daily, weekly, monthly, yearly
    frequency = Column(String, nullable=False)
    interval = Column(Integer, default=1)  # every N days/weeks/months/years
    # for weekly patterns [0=Monday, 6=Sunday]
    weekdays = Column(ARRAY(Integer), nullable=True)
    end_date = Column(DateTime, nullable=True)  # when to stop recurring
    max_occurrences = Column(Integer, nullable=True)  # max number of instances
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<RecurrencePattern(id={self.id}, frequency='{self.frequency}', interval={self.interval})>"

    def as_dict(self):
        return {
            "id": self.id,
            "frequency": self.frequency,
            "interval": self.interval,
            "weekdays": self.weekdays,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "max_occurrences": self.max_occurrences,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
