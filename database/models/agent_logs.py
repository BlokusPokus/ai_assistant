from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from .base import Base


class AgentLog(Base):
    __tablename__ = 'agent_logs'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user_input = Column(String)
    agent_response = Column(String)
    tool_called = Column(String)
    tool_output = Column(String)
    memory_used = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)
