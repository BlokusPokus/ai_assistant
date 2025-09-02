"""
Middleware components for the personal assistant framework.

📁 middleware/__init__.py
Provides middleware for request processing, correlation tracking, and other cross-cutting concerns.
"""

from .correlation_middleware import (
    CorrelationIDMiddleware,
    get_request_correlation_id
)

__all__ = [
    "CorrelationIDMiddleware",
    "get_request_correlation_id"
]
