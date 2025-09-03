"""
Webhook validation middleware for SMS Router Service.
"""

import hashlib
import hmac
import logging
from typing import Optional

from fastapi import Request

logger = logging.getLogger(__name__)


def validate_twilio_webhook(request: Request) -> bool:
    """
    Validate Twilio webhook request.

    Args:
        request: FastAPI request object

    Returns:
        True if valid, False otherwise
    """
    try:
        # For now, we'll implement basic validation
        # In production, you should implement proper Twilio signature validation

        # Check if request has required headers
        if not request.headers.get("user-agent"):
            logger.warning("Missing User-Agent header")
            return False

        # Check if User-Agent contains Twilio
        user_agent = request.headers.get("user-agent", "")
        if "twilio" not in user_agent.lower():
            logger.warning(f"Invalid User-Agent: {user_agent}")
            return False

        # Check if request method is POST
        if request.method != "POST":
            logger.warning(f"Invalid request method: {request.method}")
            return False

        # Check if request has content
        if not request.body:
            logger.warning("Empty request body")
            return False

        # Basic validation passed
        return True

    except Exception as e:
        logger.error(f"Error validating webhook: {e}")
        return False


def validate_twilio_signature(
    request: Request, auth_token: str, signature: str, url: str, params: dict
) -> bool:
    """
    Validate Twilio signature (advanced security).

    Args:
        request: FastAPI request object
        auth_token: Twilio auth token
        signature: Twilio signature header
        url: Webhook URL
        params: Request parameters

    Returns:
        True if signature is valid, False otherwise
    """
    try:
        # Sort parameters alphabetically
        sorted_params = sorted(params.items())

        # Create parameter string
        param_string = "&".join(f"{key}={value}" for key, value in sorted_params)

        # Create string to sign
        string_to_sign = url + param_string

        # Create expected signature
        expected_signature = hmac.new(
            auth_token.encode("utf-8"), string_to_sign.encode("utf-8"), hashlib.sha256
        ).hexdigest()

        # Compare signatures
        return hmac.compare_digest(signature, expected_signature)

    except Exception as e:
        logger.error(f"Error validating Twilio signature: {e}")
        return False


def get_client_ip(request: Request) -> Optional[str]:
    """
    Get client IP address from request.

    Args:
        request: FastAPI request object

    Returns:
        Client IP address or None
    """
    try:
        # Check for forwarded headers
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        # Check for real IP header
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # Get direct client IP
        if request.client:
            return request.client.host

        return None

    except Exception as e:
        logger.error(f"Error getting client IP: {e}")
        return None


def is_valid_phone_number(phone_number: str) -> bool:
    """
    Basic phone number validation.

    Args:
        phone_number: Phone number to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        if not phone_number:
            return False

        # Remove all non-digit characters except +
        cleaned = "".join(c for c in phone_number if c.isdigit() or c == "+")

        # Check if it starts with + and has reasonable length
        if not cleaned.startswith("+"):
            return False

        # Check length (international numbers are typically 7-15 digits)
        digits_only = "".join(c for c in cleaned if c.isdigit())
        if len(digits_only) < 7 or len(digits_only) > 15:
            return False

        return True

    except Exception as e:
        logger.error(f"Error validating phone number: {e}")
        return False


def rate_limit_check(
    request: Request, max_requests: int = 60, window_seconds: int = 60
) -> bool:
    """
    Basic rate limiting check.

    Args:
        request: FastAPI request object
        max_requests: Maximum requests per window
        window_seconds: Time window in seconds

    Returns:
        True if within rate limit, False otherwise
    """
    try:
        # This is a basic implementation
        # In production, you should use Redis or similar for proper rate limiting

        client_ip = get_client_ip(request)
        if not client_ip:
            return True  # Allow if we can't determine IP

        # For now, we'll just log and allow
        # TODO: Implement proper rate limiting
        logger.debug(f"Rate limit check for IP: {client_ip}")
        return True

    except Exception as e:
        logger.error(f"Error checking rate limit: {e}")
        return True  # Allow on error
