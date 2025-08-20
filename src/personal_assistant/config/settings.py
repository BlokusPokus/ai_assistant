"""
Central configuration for the personal assistant framework.

🛠 config.py
Sets up constants like vector DB settings, loop limits, tool metadata, debug flags, etc.

Constants:
    VECTOR_DB_URL: URL for vector database connection
    MAX_MEMORY_RESULTS: Maximum number of memory items to retrieve
    LOOP_LIMIT: Maximum number of iterations in agent loop
    GOOGLE_API_KEY: API key for Gemini LLM access

Description:
    Central configuration file that loads environment variables and defines
    constants used throughout the agent framework. Validates required API keys
    and provides default values for various settings.
"""
import os
from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv

# Load environment-specific config file
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
config_file = f"config/{ENVIRONMENT}.env"

# Load the appropriate config file
if os.path.exists(config_file):
    load_dotenv(config_file)
else:
    # Fallback to root .env file
    load_dotenv()


class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str = "postgresql://user:password@localhost/personal_assistant"

    # Google settings (including Gemini LLM)
    GOOGLE_API_KEY: Optional[str] = None
    YOUTUBE_API_KEY: Optional[str] = None  # YouTube Data API v3 key

    # Twilio settings
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None
    TWILIO_FROM_NUMBER: Optional[str] = None
    TWILIO_TO_NUMBER: Optional[str] = None

    # Qdrant settings
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_URL: Optional[str] = None

    # Microsoft settings
    MICROSOFT_CLIENT_SECRET: Optional[str] = None
    MICROSOFT_CLIENT_ID: Optional[str] = None
    MICROSOFT_APPLICATION_ID: Optional[str] = None

    # Notion settings
    NOTION_API_KEY: Optional[str] = None
    NOTION_DATABASE_ID: Optional[str] = None
    NOTION_WORKSPACE_ID: Optional[str] = None
    # Root page ID for creating the main table of contents page
    NOTION_ROOT_PAGE_ID: Optional[str] = None

    # Application settings
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "development"

    # Conversation management settings
    # Minutes after which conversations are considered "old"
    CONVERSATION_RESUME_WINDOW_MINUTES: int = 30

    # Logging settings
    LOG_TO_FILE: bool = True
    LOG_TO_CONSOLE: bool = True
    LOG_DIR: str = "logs"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"

    # Module-specific log levels
    CORE_LOG_LEVEL: str = "INFO"
    LLM_LOG_LEVEL: str = "INFO"
    MEMORY_LOG_LEVEL: str = "INFO"
    RAG_LOG_LEVEL: str = "INFO"
    TOOLS_LOG_LEVEL: str = "INFO"
    TYPES_LOG_LEVEL: str = "INFO"

    # Logging override environment variables (optional)
    PA_LOG_LEVEL: Optional[str] = None
    PA_CORE_LOG_LEVEL: Optional[str] = None
    PA_LLM_LOG_LEVEL: Optional[str] = None
    PA_MEMORY_LOG_LEVEL: Optional[str] = None
    PA_RAG_LOG_LEVEL: Optional[str] = None
    PA_TOOLS_LOG_LEVEL: Optional[str] = None
    PA_TYPES_LOG_LEVEL: Optional[str] = None

    # Celery settings
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Authentication settings
    JWT_SECRET_KEY: Optional[str] = None
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_SALT_ROUNDS: int = 12

    # MFA Configuration
    MFA_TOTP_ISSUER: str = "Personal Assistant TDAH"
    MFA_TOTP_WINDOW: int = 1                    # 30-second window tolerance
    MFA_SMS_RATE_LIMIT: int = 3                 # Max SMS attempts per window
    MFA_SMS_RATE_WINDOW_MINUTES: int = 10       # Rate limiting window
    MFA_BACKUP_CODES_COUNT: int = 10            # Number of backup codes
    MFA_TRUSTED_DEVICE_DAYS: int = 30           # Remember trusted devices

    # Session Management
    SESSION_EXPIRY_HOURS: int = 24              # Session lifetime
    SESSION_MAX_CONCURRENT: int = 5              # Max sessions per user
    SESSION_REDIS_DB: int = 1                    # Redis database for sessions
    SESSION_CLEANUP_INTERVAL: int = 3600         # Cleanup interval in seconds

    # Security Settings
    SECURITY_AUDIT_ENABLED: bool = True          # Enable security event logging
    SECURITY_IP_WHITELIST: str = ""              # IP addresses to trust
    SECURITY_DEVICE_TRACKING: bool = True        # Track device information

    # Rate limiting settings
    RATE_LIMIT_LOGIN_ATTEMPTS: int = 5
    RATE_LIMIT_LOGIN_WINDOW_MINUTES: int = 15
    RATE_LIMIT_TOKEN_REFRESH_PER_HOUR: int = 10
    RATE_LIMIT_REGISTRATION_PER_HOUR: int = 3

    # Vector database settings
    VECTOR_DB_URL: str = "http://localhost:6333"
    MAX_MEMORY_RESULTS: int = 15
    LOOP_LIMIT: int = 20

    # State management settings
    DEFAULT_MAX_MEMORY_CONTEXT_SIZE: int = 20  # Maximum items in memory_context
    # Maximum items in conversation_history
    DEFAULT_MAX_CONVERSATION_HISTORY_SIZE: int = 20
    DEFAULT_MAX_HISTORY_SIZE: int = 20  # Maximum items in history
    DEFAULT_CONTEXT_WINDOW_SIZE: int = 10  # Recent items to keep in context

    # RAG Configuration
    RAG_MAX_CONTEXT_LENGTH: int = 2000
    RAG_NOTION_INDEXING_ENABLED: bool = True
    RAG_BATCH_INDEX_SIZE: int = 10
    RAG_EMBEDDING_CACHE_SIZE: int = 1000
    RAG_EMBEDDING_CACHE_TTL: int = 3600  # 1 hour in seconds
    RAG_MAX_RESULTS: int = 5  # Maximum results to return from RAG queries

    class Config:
        env_file = config_file
        case_sensitive = False
        extra = "allow"  # Allow extra fields from environment variables


# Global settings instance
settings = Settings()
GEMINI_API_KEY = settings.GOOGLE_API_KEY or os.getenv("GOOGLE_API_KEY")
