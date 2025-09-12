"""
SMS Error Classification System

This module classifies SMS errors for appropriate retry strategies.
"""

from enum import Enum
from typing import Dict, Optional


class RetryStrategy(Enum):
    """Retry strategies for different error types."""
    IMMEDIATE = "immediate"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    NO_RETRY = "no_retry"


class SMSErrorClassifier:
    """Classifies SMS errors for appropriate retry strategies."""

    # Twilio error codes that should be retried
    RETRYABLE_ERRORS: Dict[str, Dict[str, any]] = {
        '30001': {
            'description': 'Temporary network issue',
            'strategy': RetryStrategy.EXPONENTIAL_BACKOFF,
            'max_retries': 3,
            'base_delay': 60
        },
        '30002': {
            'description': 'Temporary service unavailable',
            'strategy': RetryStrategy.EXPONENTIAL_BACKOFF,
            'max_retries': 3,
            'base_delay': 120
        },
        '30003': {
            'description': 'Rate limit exceeded',
            'strategy': RetryStrategy.LINEAR_BACKOFF,
            'max_retries': 2,
            'base_delay': 300
        },
        '30004': {
            'description': 'Temporary carrier issue',
            'strategy': RetryStrategy.EXPONENTIAL_BACKOFF,
            'max_retries': 2,
            'base_delay': 180
        },
        '30005': {
            'description': 'Temporary message queue full',
            'strategy': RetryStrategy.EXPONENTIAL_BACKOFF,
            'max_retries': 3,
            'base_delay': 90
        }
    }

    # Twilio error codes that should NOT be retried
    NON_RETRYABLE_ERRORS: Dict[str, str] = {
        '21211': 'Invalid phone number format',
        '21214': 'Invalid message body',
        '21610': 'Message blocked by carrier',
        '21614': 'Message body contains invalid characters',
        '21617': 'Message body is too long',
        '30006': 'Invalid phone number',
        '30007': 'Phone number is not a mobile number',
        '30008': 'Phone number is not reachable'
    }

    @classmethod
    def is_retryable(cls, error_code: str) -> bool:
        """Check if an error code should be retried."""
        return error_code in cls.RETRYABLE_ERRORS

    @classmethod
    def get_retry_strategy(cls, error_code: str) -> Optional[Dict[str, any]]:
        """Get retry strategy for an error code."""
        return cls.RETRYABLE_ERRORS.get(error_code)

    @classmethod
    def get_error_description(cls, error_code: str) -> str:
        """Get human-readable description of error code."""
        if error_code in cls.RETRYABLE_ERRORS:
            return cls.RETRYABLE_ERRORS[error_code]['description']
        elif error_code in cls.NON_RETRYABLE_ERRORS:
            return cls.NON_RETRYABLE_ERRORS[error_code]
        else:
            return f"Unknown error code: {error_code}"

    @classmethod
    def calculate_retry_delay(cls, error_code: str, retry_count: int) -> int:
        """Calculate retry delay based on error code and retry count."""
        strategy_info = cls.get_retry_strategy(error_code)
        if not strategy_info:
            return 0

        base_delay = strategy_info['base_delay']
        strategy = strategy_info['strategy']

        if strategy == RetryStrategy.IMMEDIATE:
            return 0
        elif strategy == RetryStrategy.LINEAR_BACKOFF:
            return base_delay * (retry_count + 1)
        elif strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            return base_delay * (2 ** retry_count)
        else:
            return 0
