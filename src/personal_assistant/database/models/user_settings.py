from sqlalchemy import Column, ForeignKey, Integer, String

from .base import Base


class UserSetting(Base):
    __tablename__ = 'user_settings'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    key = Column(String, nullable=False)
    value = Column(String)
