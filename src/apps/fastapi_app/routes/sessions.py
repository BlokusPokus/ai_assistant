"""
Session Management Routes.

This module provides endpoints for:
- Listing user sessions
- Invalidating specific sessions
- Session statistics and management
- Device tracking and security
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any

from personal_assistant.database.session import AsyncSessionLocal
from personal_assistant.database.models.users import User
from personal_assistant.database.models.mfa_models import SecurityEvent
from personal_assistant.auth.session_service import SessionService
from personal_assistant.config.redis import get_async_session_redis

# Create router
router = APIRouter(prefix="/api/v1/sessions", tags=["Sessions"])

# Pydantic models for request/response


class SessionInfo(BaseModel):
    """Session information model."""
    session_id: str
    device_info: Optional[Dict[str, Any]]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: str
    last_accessed: str
    expires_at: str
    is_active: bool
    session_type: str


class SessionStats(BaseModel):
    """Session statistics model."""
    total_sessions: int
    active_sessions: int
    can_create_new: bool
    oldest_session: Optional[str]
    newest_session: Optional[str]
    sessions_remaining: int


class InvalidateSessionRequest(BaseModel):
    """Request model for invalidating a session."""
    session_id: str


class InvalidateAllSessionsRequest(BaseModel):
    """Request model for invalidating all user sessions."""
    exclude_current: bool = True

# Dependencies


async def get_db() -> AsyncSession:
    """Get database session."""
    async with AsyncSessionLocal() as session:
        yield session


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user."""
    # This would be implemented with your existing JWT authentication
    # For now, we'll use a placeholder
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="JWT authentication not yet integrated with session management"
    )


async def get_session_service() -> SessionService:
    """Get session service instance."""
    redis_client = get_async_session_redis()
    if not redis_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Session service unavailable"
        )
    return SessionService(redis_client)


@router.get("/", response_model=List[SessionInfo])
async def get_user_sessions(
    request: Request,
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service)
):
    """Get all active sessions for the current user."""
    try:
        sessions = await session_service.get_user_sessions(str(current_user.id))

        # Filter sensitive information and format response
        session_list = []
        for session in sessions:
            # Create safe device info
            device_info = session.get('device_info', {})
            safe_device_info = {
                'browser': device_info.get('browser'),
                'os': device_info.get('os'),
                'device': device_info.get('device'),
                'platform': device_info.get('platform')
            }

            session_info = SessionInfo(
                session_id=session['session_id'],
                device_info=safe_device_info,
                ip_address=session.get('ip_address'),
                user_agent=session.get('user_agent'),
                created_at=session['created_at'],
                last_accessed=session['last_accessed'],
                expires_at=session['expires_at'],
                is_active=session.get('is_active', True),
                session_type=session.get('session_type', 'web')
            )
            session_list.append(session_info)

        return session_list

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get sessions: {str(e)}"
        )


@router.get("/stats", response_model=SessionStats)
async def get_session_stats(
    request: Request,
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service)
):
    """Get session statistics for the current user."""
    try:
        stats = await session_service.get_session_stats(str(current_user.id))
        return SessionStats(**stats)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session stats: {str(e)}"
        )


@router.delete("/{session_id}")
async def invalidate_session(
    session_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
    db: AsyncSession = Depends(get_db)
):
    """Invalidate a specific session."""
    try:
        # Get session to verify ownership
        session = await session_service.get_session(session_id)
        if not session or session['user_id'] != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )

        # Invalidate session
        success = await session_service.invalidate_session(session_id)

        if success:
            # Log security event
            security_event = SecurityEvent(
                user_id=current_user.id,
                event_type="session_invalidated",
                event_data={
                    "session_id": session_id,
                    "method": "manual",
                    "device_info": session.get('device_info')
                },
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                severity="info"
            )
            db.add(security_event)
            await db.commit()

            return {"message": "Session invalidated successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to invalidate session"
            )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to invalidate session: {str(e)}"
        )


@router.post("/invalidate-all")
async def invalidate_all_sessions(
    request: InvalidateAllSessionsRequest,
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
    db: AsyncSession = Depends(get_db)
):
    """Invalidate all sessions for the current user (except current if specified)."""
    try:
        # Get current session ID from request headers or context
        # For now, we'll invalidate all sessions
        current_session_id = None  # TODO: Extract from JWT or request context

        if request.exclude_current and current_session_id:
            invalidated_count = await session_service.invalidate_user_sessions(
                str(current_user.id),
                exclude_session_id=current_session_id
            )
        else:
            invalidated_count = await session_service.invalidate_user_sessions(
                str(current_user.id)
            )

        # Log security event
        security_event = SecurityEvent(
            user_id=current_user.id,
            event_type="all_sessions_invalidated",
            event_data={
                "invalidated_count": invalidated_count,
                "exclude_current": request.exclude_current
            },
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            severity="warning"
        )
        db.add(security_event)
        await db.commit()

        return {
            "message": f"Invalidated {invalidated_count} sessions successfully",
            "invalidated_count": invalidated_count
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to invalidate sessions: {str(e)}"
        )


@router.post("/extend/{session_id}")
async def extend_session(
    session_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
    db: AsyncSession = Depends(get_db),
    hours: Optional[int] = None
):
    """Extend session expiration time."""
    try:
        # Get session to verify ownership
        session = await session_service.get_session(session_id)
        if not session or session['user_id'] != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )

        # Extend session
        success = await session_service.extend_session(session_id, hours)

        if success:
            # Log security event
            security_event = SecurityEvent(
                user_id=current_user.id,
                event_type="session_extended",
                event_data={
                    "session_id": session_id,
                    "extension_hours": hours,
                    "new_expiry": session.get('expires_at')
                },
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                severity="info"
            )
            db.add(security_event)
            await db.commit()

            return {"message": "Session extended successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to extend session"
            )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extend session: {str(e)}"
        )


@router.get("/health")
async def check_session_service_health(
    session_service: SessionService = Depends(get_session_service)
):
    """Check session service health."""
    try:
        # Simple health check - try to access Redis
        redis_client = session_service.redis
        await redis_client.ping()

        return {
            "status": "healthy",
            "service": "session_management",
            "redis": "connected"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Session service unhealthy: {str(e)}"
        )
