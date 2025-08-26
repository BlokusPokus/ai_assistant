"""
Configuration settings for SMS Router Service.
"""

from pydantic_settings import BaseSettings
from typing import Optional

class SMSServiceSettings(BaseSettings):
    """SMS Router Service configuration settings."""
    
    # Service Configuration
    LOG_LEVEL: str = "info"
    
    # Database Configuration (inherited from main app)
    DATABASE_URL: Optional[str] = None
    
    # Twilio Configuration (inherited from main app)
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_FROM_NUMBER: Optional[str] = None
    
    # Redis Configuration (for caching)
    REDIS_URL: Optional[str] = None
    
    # Security Configuration
    WEBHOOK_SECRET: Optional[str] = None
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Performance Configuration
    CACHE_TTL_SECONDS: int = 3600  # 1 hour
    MAX_CONCURRENT_SMS: int = 100
    
    class Config:
        env_file = None  # Don't load .env file
        env_prefix = "SMS_ROUTER_"
        extra = "ignore"  # Ignore extra fields

# Create settings instance
settings = SMSServiceSettings()
