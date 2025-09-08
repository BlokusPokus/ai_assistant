"""
Log filter to reduce embedding noise in logs.

This filter helps reduce verbose embedding-related log messages that can clutter
the logs while keeping important error and warning messages.
"""

import logging
import re
from typing import Optional


class EmbeddingNoiseFilter(logging.Filter):
    """
    Filter to reduce embedding-related log noise.
    
    This filter removes or downgrades verbose embedding messages while
    preserving important error and warning messages.
    """
    
    def __init__(self, name: str = ""):
        super().__init__(name)
        
        # Patterns to filter out (case-insensitive)
        self.noise_patterns = [
            r"generated embedding of length \d+ for text of length \d+",
            r"embedding cache hit for text of length \d+",
            r"embedding cache miss for text of length \d+",
            r"cached embedding for text of length \d+",
            r"creating embedding for text of length: \d+",
            r"embedding created with length: \d+",
            r"generating embedding for message \d+",
            r"embedding generated for message \d+",
            r"generating rag embeddings for conversation \d+",
            r"rag embeddings generated for conversation \d+",
        ]
        
        # Compile patterns for better performance
        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE) for pattern in self.noise_patterns
        ]
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter log records to reduce embedding noise.
        
        Args:
            record: The log record to filter
            
        Returns:
            True if the record should be logged, False otherwise
        """
        # Always allow ERROR and CRITICAL messages
        if record.levelno >= logging.ERROR:
            return True
        
        # Always allow WARNING messages
        if record.levelno >= logging.WARNING:
            return True
        
        # Check if the message matches any noise patterns
        message = record.getMessage()
        for pattern in self.compiled_patterns:
            if pattern.search(message):
                # Filter out INFO and DEBUG embedding noise
                if record.levelno <= logging.INFO:
                    return False
        
        # Allow all other messages
        return True


class EmbeddingDebugFilter(logging.Filter):
    """
    More aggressive filter that only allows embedding errors and warnings.
    
    This filter is more restrictive and only allows critical embedding messages.
    """
    
    def __init__(self, name: str = ""):
        super().__init__(name)
        
        # Patterns for important embedding messages to keep
        self.important_patterns = [
            r"embedding.*error",
            r"embedding.*failed",
            r"embedding.*exception",
            r"no embedding returned",
            r"failed to generate embedding",
            r"embedding.*warning",
            r"embedding cache cleared",
        ]
        
        # Compile patterns for better performance
        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE) for pattern in self.important_patterns
        ]
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter log records to only allow important embedding messages.
        
        Args:
            record: The log record to filter
            
        Returns:
            True if the record should be logged, False otherwise
        """
        # Always allow ERROR and CRITICAL messages
        if record.levelno >= logging.ERROR:
            return True
        
        # Check if the message matches important patterns
        message = record.getMessage()
        for pattern in self.compiled_patterns:
            if pattern.search(message):
                return True
        
        # Filter out all other embedding messages
        if "embedding" in message.lower():
            return False
        
        # Allow all non-embedding messages
        return True


def apply_embedding_filter(logger_name: str, filter_type: str = "noise") -> None:
    """
    Apply embedding filter to a specific logger.
    
    Args:
        logger_name: Name of the logger to apply filter to
        filter_type: Type of filter ("noise" or "debug")
    """
    logger = logging.getLogger(logger_name)
    
    if filter_type == "noise":
        filter_instance = EmbeddingNoiseFilter()
    elif filter_type == "debug":
        filter_instance = EmbeddingDebugFilter()
    else:
        raise ValueError(f"Unknown filter type: {filter_type}")
    
    # Remove existing embedding filters
    for handler in logger.handlers:
        for existing_filter in handler.filters:
            if isinstance(existing_filter, (EmbeddingNoiseFilter, EmbeddingDebugFilter)):
                handler.removeFilter(existing_filter)
    
    # Add the new filter to all handlers
    for handler in logger.handlers:
        handler.addFilter(filter_instance)


def setup_embedding_logging_control() -> None:
    """
    Set up embedding logging control for all relevant loggers.
    
    This function applies embedding filters to all loggers that might
    generate embedding-related noise.
    """
    # List of loggers that might generate embedding noise
    embedding_loggers = [
        "personal_assistant.rag",
        "personal_assistant.rag.embeddings",
        "personal_assistant.rag.retriever",
        "personal_assistant.llm",
        "personal_assistant.memory",
    ]
    
    # Apply noise filter to each logger
    for logger_name in embedding_loggers:
        try:
            apply_embedding_filter(logger_name, "noise")
        except Exception as e:
            # Don't fail if logger doesn't exist
            pass


# Convenience functions for different levels of filtering
def enable_embedding_noise_filter():
    """Enable noise filtering for embedding logs."""
    setup_embedding_logging_control()


def disable_embedding_logs():
    """Disable all embedding logs except errors and warnings."""
    embedding_loggers = [
        "personal_assistant.rag",
        "personal_assistant.rag.embeddings", 
        "personal_assistant.rag.retriever",
        "personal_assistant.llm",
    ]
    
    for logger_name in embedding_loggers:
        try:
            logger = logging.getLogger(logger_name)
            logger.setLevel(logging.WARNING)
        except Exception:
            pass


def set_embedding_log_level(level: str):
    """
    Set the log level for embedding-related loggers.
    
    Args:
        level: Log level ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
    """
    embedding_loggers = [
        "personal_assistant.rag",
        "personal_assistant.rag.embeddings",
        "personal_assistant.rag.retriever", 
        "personal_assistant.llm",
    ]
    
    level_num = getattr(logging, level.upper(), logging.INFO)
    
    for logger_name in embedding_loggers:
        try:
            logger = logging.getLogger(logger_name)
            logger.setLevel(level_num)
        except Exception:
            pass
