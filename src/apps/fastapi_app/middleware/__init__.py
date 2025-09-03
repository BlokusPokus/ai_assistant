"""
FastAPI middleware for authentication and security.

This module provides authentication middleware, rate limiting,
and other security-related middleware components.
"""

from .auth import AuthMiddleware
from .rate_limiting import RateLimitingMiddleware

__all__ = ["AuthMiddleware", "RateLimitingMiddleware"]
