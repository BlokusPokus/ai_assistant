"""
Session Management Service for user sessions.

This service provides:
- Redis-based session storage
- Session lifecycle management
- Device tracking and security
- Concurrent session limits
"""

import json
import secrets
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import redis.asyncio as redis
from personal_assistant.config.settings import settings


class SessionService:
    """Service for managing user sessions."""

    def __init__(self, redis_client: redis.Redis):
        """
        Initialize session service.

        Args:
            redis_client: Redis client for session storage
        """
        self.redis = redis_client
        self.session_prefix = "session:"
        self.user_sessions_prefix = "user_sessions:"
        self.session_expiry_hours = settings.SESSION_EXPIRY_HOURS
        self.max_concurrent_sessions = settings.SESSION_MAX_CONCURRENT

    async def create_session(self, user_id: int, device_info: Dict[str, Any]) -> str:
        """
        Create a new session for a user.

        Args:
            user_id: User identifier
            device_info: Device information dictionary

        Returns:
            Session ID

        Raises:
            ValueError: If maximum concurrent sessions reached
        """
        # Check concurrent session limit
        if not await self.enforce_session_limits(user_id):
            raise ValueError(
                f"Maximum concurrent sessions ({self.max_concurrent_sessions}) reached. "
                "Please close another session first."
            )

        # Generate cryptographically secure session ID
        session_id = secrets.token_urlsafe(32)

        # Create session data
        session_data = {
            'user_id': user_id,
            'device_info': device_info,
            'created_at': datetime.utcnow().isoformat(),
            'last_accessed': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(hours=self.session_expiry_hours)).isoformat(),
            'is_active': True,
            'session_type': 'web'  # Can be 'web', 'mobile', 'api', etc.
        }

        # Store in Redis with TTL
        session_key = f"{self.session_prefix}{session_id}"
        ttl_seconds = self.session_expiry_hours * 3600

        await self.redis.setex(
            session_key,
            ttl_seconds,
            json.dumps(session_data)
        )

        # Track user sessions
        user_sessions_key = f"{self.user_sessions_prefix}{user_id}"
        await self.redis.sadd(user_sessions_key, session_id)
        await self.redis.expire(user_sessions_key, ttl_seconds)

        return session_id

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve session data by ID.

        Args:
            session_id: Session identifier

        Returns:
            Session data or None if not found/expired
        """
        session_key = f"{self.session_prefix}{session_id}"
        session_data = await self.redis.get(session_key)

        if not session_data:
            return None

        try:
            session = json.loads(session_data)
        except json.JSONDecodeError:
            # Invalid session data, remove it
            await self.redis.delete(session_key)
            return None

        # Check if expired
        if datetime.fromisoformat(session['expires_at']) < datetime.utcnow():
            await self.invalidate_session(session_id)
            return None

        # Update last accessed time
        session['last_accessed'] = datetime.utcnow().isoformat()

        # Refresh TTL
        ttl_seconds = self.session_expiry_hours * 3600
        await self.redis.setex(
            session_key,
            ttl_seconds,
            json.dumps(session)
        )

        return session

    async def update_session(self, session_id: str, data: Dict[str, Any]) -> bool:
        """
        Update session data.

        Args:
            session_id: Session identifier
            data: Data to update

        Returns:
            True if successful, False otherwise
        """
        session_key = f"{self.session_prefix}{session_id}"
        session_data = await self.redis.get(session_key)

        if not session_data:
            return False

        try:
            session = json.loads(session_data)
        except json.JSONDecodeError:
            return False

        # Update session data
        session.update(data)
        session['last_accessed'] = datetime.utcnow().isoformat()

        # Refresh TTL
        ttl_seconds = self.session_expiry_hours * 3600
        await self.redis.setex(
            session_key,
            ttl_seconds,
            json.dumps(session)
        )

        return True

    async def invalidate_session(self, session_id: str) -> bool:
        """
        Invalidate a session.

        Args:
            session_id: Session identifier

        Returns:
            True if successful, False otherwise
        """
        session_key = f"{self.session_prefix}{session_id}"
        session_data = await self.redis.get(session_key)

        if not session_data:
            return False

        try:
            session = json.loads(session_data)
            user_id = session['user_id']
        except (json.JSONDecodeError, KeyError):
            # Invalid session data, just remove it
            await self.redis.delete(session_key)
            return False

        # Remove from Redis
        await self.redis.delete(session_key)

        # Remove from user sessions
        user_sessions_key = f"{self.user_sessions_prefix}{user_id}"
        await self.redis.srem(user_sessions_key, session_id)

        return True

    async def get_user_sessions(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get all active sessions for a user.

        Args:
            user_id: User identifier

        Returns:
            List of active sessions
        """
        user_sessions_key = f"{self.user_sessions_prefix}{user_id}"
        session_ids = await self.redis.smembers(user_sessions_key)

        sessions = []
        for session_id in session_ids:
            session = await self.get_session(session_id)
            if session:
                sessions.append(session)

        return sessions

    async def enforce_session_limits(self, user_id: int) -> bool:
        """
        Check if user can create a new session.

        Args:
            user_id: User identifier

        Returns:
            True if can create new session, False otherwise
        """
        current_sessions = await self.get_user_sessions(user_id)
        return len(current_sessions) < self.max_concurrent_sessions

    async def invalidate_user_sessions(self, user_id: int, exclude_session_id: Optional[str] = None) -> int:
        """
        Invalidate all sessions for a user (e.g., on password change).

        Args:
            user_id: User identifier
            exclude_session_id: Session ID to exclude from invalidation

        Returns:
            Number of sessions invalidated
        """
        user_sessions_key = f"{self.user_sessions_prefix}{user_id}"
        session_ids = await self.redis.smembers(user_sessions_key)

        invalidated_count = 0

        for session_id in session_ids:
            if session_id != exclude_session_id:
                if await self.invalidate_session(session_id):
                    invalidated_count += 1

        return invalidated_count

    async def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions.

        Returns:
            Number of sessions cleaned up
        """
        # This is a simplified cleanup - in production, you might want
        # to use Redis SCAN for better performance with large datasets

        # For now, we rely on Redis TTL for automatic cleanup
        # This method can be enhanced with periodic cleanup tasks

        return 0

    async def get_session_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Get session statistics for a user.

        Args:
            user_id: User identifier

        Returns:
            Session statistics
        """
        sessions = await self.get_user_sessions(user_id)

        if not sessions:
            return {
                'total_sessions': 0,
                'active_sessions': 0,
                'can_create_new': True,
                'oldest_session': None,
                'newest_session': None
            }

        # Calculate statistics
        active_sessions = [s for s in sessions if s.get('is_active', False)]
        oldest_session = min(sessions, key=lambda x: x['created_at'])
        newest_session = max(sessions, key=lambda x: x['last_accessed'])

        return {
            'total_sessions': len(sessions),
            'active_sessions': len(active_sessions),
            'can_create_new': len(sessions) < self.max_concurrent_sessions,
            'oldest_session': oldest_session['created_at'],
            'newest_session': newest_session['last_accessed'],
            'sessions_remaining': max(0, self.max_concurrent_sessions - len(sessions))
        }

    async def extend_session(self, session_id: str, hours: Optional[int] = None) -> bool:
        """
        Extend session expiration time.

        Args:
            session_id: Session identifier
            hours: Hours to extend (defaults to session expiry hours)

        Returns:
            True if successful, False otherwise
        """
        if hours is None:
            hours = self.session_expiry_hours

        session_key = f"{self.session_prefix}{session_id}"
        session_data = await self.redis.get(session_key)

        if not session_data:
            return False

        try:
            session = json.loads(session_data)
        except json.JSONDecodeError:
            return False

        # Extend expiration
        new_expiry = datetime.utcnow() + timedelta(hours=hours)
        session['expires_at'] = new_expiry.isoformat()
        session['last_accessed'] = datetime.utcnow().isoformat()

        # Update with new TTL
        ttl_seconds = hours * 3600
        await self.redis.setex(
            session_key,
            ttl_seconds,
            json.dumps(session)
        )

        # Update user sessions TTL
        user_id = session['user_id']
        user_sessions_key = f"{self.user_sessions_prefix}{user_id}"
        await self.redis.expire(user_sessions_key, ttl_seconds)

        return True

    async def get_session_by_device(self, user_id: int, device_hash: str) -> Optional[Dict[str, Any]]:
        """
        Find session by device hash for a user.

        Args:
            user_id: User identifier
            device_hash: Device hash to search for

        Returns:
            Session data or None if not found
        """
        sessions = await self.get_user_sessions(user_id)

        for session in sessions:
            device_info = session.get('device_info', {})
            if device_info.get('device_hash') == device_hash:
                return session

        return None
