"""
SMS Router Service database models.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, JSON, Index
from sqlalchemy.orm import relationship

from ...database.models.base import Base


class SMSRouterConfig(Base):
    """Configuration for SMS routing behavior."""
    __tablename__ = 'sms_router_configs'

    id = Column(Integer, primary_key=True)
    config_key = Column(String(100), unique=True, nullable=False)
    config_value = Column(Text, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<SMSRouterConfig(id={self.id}, key='{self.config_key}', active={self.is_active})>"


class SMSUsageLog(Base):
    """Log of SMS usage for analytics and billing."""
    __tablename__ = 'sms_usage_logs'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    phone_number = Column(String(20), nullable=False)
    # 'inbound' or 'outbound'
    message_direction = Column(String(10), nullable=False)
    message_length = Column(Integer, nullable=False)
    message_content = Column(Text)
    success = Column(Boolean, default=True)
    processing_time_ms = Column(Integer)
    error_message = Column(Text)
    country_code = Column(String(10), default="US")  # Country code for pricing
    sms_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="sms_usage_logs")

    def __repr__(self):
        return f"<SMSUsageLog(id={self.id}, user_id={self.user_id}, direction='{self.message_direction}')>"


class UserPhoneMapping(Base):
    """Additional phone number mappings for users (extends users.phone_number)."""
    __tablename__ = 'user_phone_mappings'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    phone_number = Column(String(20), nullable=False)
    is_primary = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    verification_method = Column(String(50))  # 'sms', 'manual', 'oauth'
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="phone_mappings")

    def __repr__(self):
        return f"<UserPhoneMapping(id={self.id}, user_id={self.user_id}, phone='{self.phone_number}')>"


# Create indexes for performance
Index('idx_sms_usage_logs_user_id', SMSUsageLog.user_id)
Index('idx_sms_usage_logs_phone_number', SMSUsageLog.phone_number)
Index('idx_sms_usage_logs_created_at', SMSUsageLog.created_at)
Index('idx_user_phone_mappings_user_id', UserPhoneMapping.user_id)
Index('idx_user_phone_mappings_phone_number', UserPhoneMapping.phone_number)
Index('idx_sms_router_configs_key', SMSRouterConfig.config_key)
