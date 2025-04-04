from sqlalchemy import Column, Integer, String
from .base import Base


class NotificationTemplate(Base):
    __tablename__ = 'notification_templates'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    content = Column(String)
