# Configure module logger
from personal_assistant.config.logging_config import get_logger

from .agent import AgentCore

logger = get_logger("core")

__all__ = ["AgentCore", "logger"]
