"""
Correlation ID middleware for FastAPI applications.

📁 middleware/correlation_middleware.py
Provides request correlation tracking across all services and components.
"""

import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from ..logging import set_correlation_id, get_correlation_id


class CorrelationIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add correlation IDs to all requests for tracing and debugging.

    This middleware:
    - Generates a unique correlation ID for each request
    - Stores it in the request context
    - Adds it to response headers
    - Makes it available throughout the request lifecycle
    """

    def __init__(self, app: ASGIApp, header_name: str = "X-Correlation-ID"):
        """
        Initialize the correlation ID middleware.

        Args:
            app: The ASGI application
            header_name: Name of the correlation ID header
        """
        super().__init__(app)
        self.header_name = header_name

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process the request and add correlation ID.

        Args:
            request: The incoming request
            call_next: The next middleware/handler in the chain

        Returns:
            Response with correlation ID header
        """
        # Check if correlation ID is already provided in request headers
        correlation_id = request.headers.get(self.header_name)

        if not correlation_id:
            # Generate a new correlation ID
            correlation_id = str(uuid.uuid4())

        # Set the correlation ID in the context
        set_correlation_id(correlation_id)

        # Store in request state for access in handlers
        request.state.correlation_id = correlation_id

        # Process the request
        response = await call_next(request)

        # Add correlation ID to response headers
        response.headers[self.header_name] = correlation_id

        return response


def get_request_correlation_id(request: Request) -> str:
    """
    Get the correlation ID from the request state.

    Args:
        request: FastAPI request object

    Returns:
        Correlation ID for the request
    """
    return getattr(request.state, 'correlation_id', get_correlation_id() or 'unknown')
