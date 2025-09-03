"""
Multi-Factor Authentication (MFA) routes.

This module provides endpoints for:
- TOTP MFA setup and verification
- SMS MFA setup and verification
- Backup codes management
- MFA status and configuration
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from personal_assistant.auth.decorators import require_permission
from personal_assistant.auth.mfa_service import MFAService
from personal_assistant.auth.sms_mfa import SMSMFAService
from personal_assistant.database.models.mfa_models import (
    MFAConfiguration,
    SecurityEvent,
)
from personal_assistant.database.models.users import User
from personal_assistant.database.session import AsyncSessionLocal

# Create router
router = APIRouter(prefix="/api/v1/mfa", tags=["MFA"])

# Pydantic models for request/response


class TOTPSetupRequest(BaseModel):
    """Request model for TOTP setup."""

    pass


class TOTPSetupResponse(BaseModel):
    """Response model for TOTP setup."""

    totp_secret: str
    qr_code: str
    message: str


class TOTPVerifyRequest(BaseModel):
    """Request model for TOTP verification."""

    token: str


class TOTPVerifyResponse(BaseModel):
    """Response model for TOTP verification."""

    message: str
    backup_codes: List[str]


class SMSMFASetupRequest(BaseModel):
    """Request model for SMS MFA setup."""

    phone_number: str


class SMSMFASetupResponse(BaseModel):
    """Response model for SMS MFA setup."""

    code_id: str
    message: str


class SMSMFAVerifyRequest(BaseModel):
    """Request model for SMS MFA verification."""

    code_id: str
    code: str


class SMSMFAVerifyResponse(BaseModel):
    """Response model for SMS MFA verification."""

    message: str


class BackupCodeVerifyRequest(BaseModel):
    """Request model for backup code verification."""

    code: str


class MFAStatusResponse(BaseModel):
    """Response model for MFA status."""

    totp_enabled: bool
    sms_enabled: bool
    phone_number: Optional[str]
    backup_codes_count: int
    trusted_devices_count: int


class DisableMFARequest(BaseModel):
    """Request model for disabling MFA."""

    method: str  # 'totp' or 'sms'
    password: str  # User's password for confirmation


# Dependencies


async def get_db() -> AsyncSession:
    """Get database session."""
    async with AsyncSessionLocal() as session:
        yield session


async def get_current_user(
    request: Request, db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user."""
    # This would be implemented with your existing JWT authentication
    # For now, we'll use a placeholder
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="JWT authentication not yet integrated with MFA",
    )


# MFA Service instances
mfa_service = MFAService()
sms_mfa_service = SMSMFAService()  # TODO: Inject actual Twilio client


@router.post("/setup/totp", response_model=TOTPSetupResponse)
@require_permission("user", "update")
async def setup_totp(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Setup TOTP-based MFA for the current user."""
    try:
        # Check if MFA is already configured
        existing_config = await db.execute(
            select(MFAConfiguration).where(MFAConfiguration.user_id == current_user.id)
        )
        existing_config = existing_config.scalar_one_or_none()

        if existing_config and existing_config.totp_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="TOTP MFA is already enabled",
            )

        # Generate TOTP secret
        totp_secret = mfa_service.generate_totp_secret(str(current_user.id))

        # Generate QR code
        qr_code = mfa_service.generate_qr_code(totp_secret, current_user.email)

        # Store or update configuration
        if existing_config:
            existing_config.totp_secret = totp_secret
            existing_config.totp_enabled = False  # Will be enabled after verification
        else:
            existing_config = MFAConfiguration(
                user_id=current_user.id, totp_secret=totp_secret, totp_enabled=False
            )
            db.add(existing_config)

        await db.commit()

        # Log security event
        security_event = SecurityEvent(
            user_id=current_user.id,
            event_type="mfa_totp_setup_initiated",
            event_data={"method": "totp"},
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            severity="info",
        )
        db.add(security_event)
        await db.commit()

        return TOTPSetupResponse(
            totp_secret=totp_secret,
            qr_code=qr_code,
            message="Scan QR code with your authenticator app, then verify with a token",
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to setup TOTP: {str(e)}",
        )


@router.post("/verify/totp", response_model=TOTPVerifyResponse)
async def verify_totp(
    request: TOTPVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Verify TOTP token and enable MFA."""
    try:
        # Get MFA configuration
        mfa_config = await db.execute(
            select(MFAConfiguration).where(MFAConfiguration.user_id == current_user.id)
        )
        mfa_config = mfa_config.scalar_one_or_none()

        if not mfa_config or not mfa_config.totp_secret:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="TOTP not configured. Please setup TOTP first.",
            )

        # Verify token
        if not mfa_service.verify_totp(mfa_config.totp_secret, request.token):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid TOTP token"
            )

        # Enable MFA
        mfa_config.totp_enabled = True

        # Generate backup codes
        backup_codes = mfa_service.generate_backup_codes()
        mfa_config.backup_codes = backup_codes

        await db.commit()

        # Log security event
        security_event = SecurityEvent(
            user_id=current_user.id,
            event_type="mfa_totp_enabled",
            event_data={"method": "totp"},
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            severity="info",
        )
        db.add(security_event)
        await db.commit()

        return TOTPVerifyResponse(
            message="TOTP MFA enabled successfully", backup_codes=backup_codes
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify TOTP: {str(e)}",
        )


@router.post("/setup/sms", response_model=SMSMFASetupResponse)
async def setup_sms_mfa(
    request: SMSMFASetupRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Setup SMS-based MFA for the current user."""
    try:
        # Check if MFA is already configured
        existing_config = await db.execute(
            select(MFAConfiguration).where(MFAConfiguration.user_id == current_user.id)
        )
        existing_config = existing_config.scalar_one_or_none()

        if existing_config and existing_config.sms_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="SMS MFA is already enabled",
            )

        # Send verification code
        try:
            code_id = sms_mfa_service.send_verification_code(request.phone_number)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(e)
            )

        # Store or update configuration
        if existing_config:
            existing_config.phone_number = request.phone_number
            existing_config.sms_enabled = False  # Will be enabled after verification
        else:
            existing_config = MFAConfiguration(
                user_id=current_user.id,
                phone_number=request.phone_number,
                sms_enabled=False,
            )
            db.add(existing_config)

        await db.commit()

        # Log security event
        security_event = SecurityEvent(
            user_id=current_user.id,
            event_type="mfa_sms_setup_initiated",
            event_data={"method": "sms", "phone_number": request.phone_number},
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            severity="info",
        )
        db.add(security_event)
        await db.commit()

        return SMSMFASetupResponse(
            code_id=code_id,
            message=f"SMS verification code sent to {request.phone_number}",
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to setup SMS MFA: {str(e)}",
        )


@router.post("/verify/sms", response_model=SMSMFAVerifyResponse)
async def verify_sms_mfa(
    request: SMSMFAVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Verify SMS code and enable MFA."""
    try:
        # Get MFA configuration
        mfa_config = await db.execute(
            select(MFAConfiguration).where(MFAConfiguration.user_id == current_user.id)
        )
        mfa_config = mfa_config.scalar_one_or_none()

        if not mfa_config or not mfa_config.phone_number:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="SMS MFA not configured. Please setup SMS MFA first.",
            )

        # Verify code
        if not sms_mfa_service.verify_code(request.code_id, request.code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid SMS verification code",
            )

        # Enable MFA
        mfa_config.sms_enabled = True

        await db.commit()

        # Log security event
        security_event = SecurityEvent(
            user_id=current_user.id,
            event_type="mfa_sms_enabled",
            event_data={"method": "sms"},
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            severity="info",
        )
        db.add(security_event)
        await db.commit()

        return SMSMFAVerifyResponse(message="SMS MFA enabled successfully")

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify SMS MFA: {str(e)}",
        )


@router.post("/verify/backup")
async def verify_backup_code(
    request: BackupCodeVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Verify backup code for account recovery."""
    try:
        # Get MFA configuration
        mfa_config = await db.execute(
            select(MFAConfiguration).where(MFAConfiguration.user_id == current_user.id)
        )
        mfa_config = mfa_config.scalar_one_or_none()

        if not mfa_config or not mfa_config.backup_codes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No backup codes configured",
            )

        # Verify backup code
        if not mfa_service.verify_backup_code(
            str(current_user.id), request.code, mfa_config.backup_codes
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid backup code"
            )

        # Update configuration (backup code was consumed)
        await db.commit()

        # Log security event
        security_event = SecurityEvent(
            user_id=current_user.id,
            event_type="mfa_backup_code_used",
            event_data={"method": "backup_code"},
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            severity="warning",
        )
        db.add(security_event)
        await db.commit()

        return {"message": "Backup code verified successfully"}

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify backup code: {str(e)}",
        )


@router.get("/status", response_model=MFAStatusResponse)
@require_permission("user", "read")
async def get_mfa_status(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get MFA status for the current user."""
    try:
        # Get MFA configuration
        mfa_config = await db.execute(
            select(MFAConfiguration).where(MFAConfiguration.user_id == current_user.id)
        )
        mfa_config = mfa_config.scalar_one_or_none()

        if not mfa_config:
            return MFAStatusResponse(
                totp_enabled=False,
                sms_enabled=False,
                phone_number=None,
                backup_codes_count=0,
                trusted_devices_count=0,
            )

        return MFAStatusResponse(
            totp_enabled=mfa_config.totp_enabled or False,
            sms_enabled=mfa_config.sms_enabled or False,
            phone_number=mfa_config.phone_number,
            backup_codes_count=len(mfa_config.backup_codes)
            if mfa_config.backup_codes
            else 0,
            trusted_devices_count=len(mfa_config.trusted_devices)
            if mfa_config.trusted_devices
            else 0,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get MFA status: {str(e)}",
        )


@router.post("/disable")
@require_permission("user", "update")
async def disable_mfa(
    request_obj: Request,
    request: DisableMFARequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Disable MFA for the current user."""
    try:
        # TODO: Verify password before disabling MFA
        # For now, we'll skip password verification

        # Get MFA configuration
        mfa_config = await db.execute(
            select(MFAConfiguration).where(MFAConfiguration.user_id == current_user.id)
        )
        mfa_config = mfa_config.scalar_one_or_none()

        if not mfa_config:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="MFA not configured"
            )

        # Disable specified method
        if request.method.lower() == "totp":
            mfa_config.totp_enabled = False
            mfa_config.totp_secret = None
            mfa_config.backup_codes = None
        elif request.method.lower() == "sms":
            mfa_config.sms_enabled = False
            mfa_config.phone_number = None
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid MFA method. Use 'totp' or 'sms'",
            )

        await db.commit()

        # Log security event
        security_event = SecurityEvent(
            user_id=current_user.id,
            event_type="mfa_disabled",
            event_data={"method": request.method.lower()},
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            severity="warning",
        )
        db.add(security_event)
        await db.commit()

        return {"message": f"{request.method.upper()} MFA disabled successfully"}

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to disable MFA: {str(e)}",
        )


@router.post("/regenerate-backup-codes")
async def regenerate_backup_codes(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Regenerate backup codes for the current user."""
    try:
        # Get MFA configuration
        mfa_config = await db.execute(
            select(MFAConfiguration).where(MFAConfiguration.user_id == current_user.id)
        )
        mfa_config = mfa_config.scalar_one_or_none()

        if not mfa_config or not mfa_config.totp_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="TOTP MFA must be enabled to use backup codes",
            )

        # Generate new backup codes
        new_backup_codes = mfa_service.generate_backup_codes()
        mfa_config.backup_codes = new_backup_codes

        await db.commit()

        # Log security event
        security_event = SecurityEvent(
            user_id=current_user.id,
            event_type="mfa_backup_codes_regenerated",
            event_data={"method": "totp"},
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            severity="info",
        )
        db.add(security_event)
        await db.commit()

        return {
            "message": "Backup codes regenerated successfully",
            "backup_codes": new_backup_codes,
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to regenerate backup codes: {str(e)}",
        )
