"""
Admin routes for SMS Router Service.
"""

import logging
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from personal_assistant.auth.decorators import require_permission
from personal_assistant.database.session import AsyncSessionLocal
from personal_assistant.sms_router.models.sms_models import (
    SMSRouterConfig,
    SMSUsageLog,
    UserPhoneMapping,
)
from personal_assistant.sms_router.services.routing_engine import SMSRoutingEngine

logger = logging.getLogger(__name__)
router = APIRouter()


async def get_db() -> AsyncSession:
    """Get database session."""
    async with AsyncSessionLocal() as session:
        yield session


@router.get("/status")
@require_permission("system", "view_sms_status")
async def get_sms_router_status(
    request: Request, routing_engine: SMSRoutingEngine = Depends()
):
    """Get comprehensive status of SMS Router Service."""
    try:
        health_status = await routing_engine.health_check()
        routing_stats = await routing_engine.get_routing_stats()

        return {
            "service": "SMS Router Service",
            "status": health_status,
            "statistics": routing_stats,
            "endpoints": {
                "webhook": "/sms-router/webhook/sms",
                "health": "/sms-router/webhook/health",
                "stats": "/sms-router/webhook/stats",
            },
        }
    except Exception as e:
        logger.error(f"Error getting SMS Router status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get service status")


@router.get("/usage")
@require_permission("system", "view_sms_usage")
async def get_sms_usage(
    request: Request,
    db: AsyncSession = Depends(get_db),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """Get SMS usage logs."""
    try:
        # Get total count
        count_result = await db.execute(select(SMSUsageLog))
        total_count = len(count_result.scalars().all())

        # Get paginated results
        result = await db.execute(
            select(SMSUsageLog)
            .order_by(desc(SMSUsageLog.created_at))
            .limit(limit)
            .offset(offset)
        )

        usage_logs = result.scalars().all()

        return {
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "logs": [
                {
                    "id": log.id,
                    "user_id": log.user_id,
                    "phone_number": log.phone_number,
                    "direction": log.message_direction,
                    "length": log.message_length,
                    "success": log.success,
                    "processing_time_ms": log.processing_time_ms,
                    "created_at": log.created_at.isoformat()
                    if log.created_at
                    else None,
                }
                for log in usage_logs
            ],
        }
    except Exception as e:
        logger.error(f"Error getting SMS usage: {e}")
        raise HTTPException(status_code=500, detail="Failed to get usage logs")


@router.get("/phone-mappings")
@require_permission("system", "view_phone_mappings")
async def get_phone_mappings(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
):
    """Get phone number mappings."""
    try:
        if user_id:
            # Get mappings for specific user
            result = await db.execute(
                select(UserPhoneMapping).where(UserPhoneMapping.user_id == user_id)
            )
        else:
            # Get all mappings
            result = await db.execute(select(UserPhoneMapping))

        mappings = result.scalars().all()

        return {
            "mappings": [
                {
                    "id": mapping.id,
                    "user_id": mapping.user_id,
                    "phone_number": mapping.phone_number,
                    "is_primary": mapping.is_primary,
                    "is_verified": mapping.is_verified,
                    "verification_method": mapping.verification_method,
                    "created_at": mapping.created_at.isoformat()
                    if mapping.created_at
                    else None,
                }
                for mapping in mappings
            ]
        }
    except Exception as e:
        logger.error(f"Error getting phone mappings: {e}")
        raise HTTPException(status_code=500, detail="Failed to get phone mappings")


@router.post("/phone-mappings")
@require_permission("system", "manage_phone_mappings")
async def create_phone_mapping(
    request: Request,
    user_id: int = Query(..., description="User ID"),
    phone_number: str = Query(..., description="Phone number to add"),
    is_primary: bool = Query(False, description="Whether this is the primary number"),
    verification_method: str = Query("manual", description="Verification method"),
    db: AsyncSession = Depends(get_db),
):
    """Create a new phone number mapping."""
    try:
        from personal_assistant.sms_router.services.user_identification import (
            UserIdentificationService,
        )

        user_identification = UserIdentificationService()

        success = await user_identification.add_phone_mapping(
            user_id, phone_number, is_primary, verification_method
        )

        if success:
            return {
                "message": "Phone mapping created successfully",
                "user_id": user_id,
                "phone_number": phone_number,
            }
        else:
            raise HTTPException(
                status_code=400, detail="Failed to create phone mapping"
            )

    except Exception as e:
        logger.error(f"Error creating phone mapping: {e}")
        raise HTTPException(status_code=500, detail="Failed to create phone mapping")


@router.get("/config")
@require_permission("system", "view_sms_config")
async def get_sms_config(request: Request, db: AsyncSession = Depends(get_db)):
    """Get SMS Router configuration."""
    try:
        result = await db.execute(select(SMSRouterConfig))
        configs = result.scalars().all()

        return {
            "configs": [
                {
                    "key": config.config_key,
                    "value": config.config_value,
                    "description": config.description,
                    "is_active": config.is_active,
                    "updated_at": config.updated_at.isoformat()
                    if config.updated_at
                    else None,
                }
                for config in configs
            ]
        }
    except Exception as e:
        logger.error(f"Error getting SMS config: {e}")
        raise HTTPException(status_code=500, detail="Failed to get configuration")


@router.post("/config")
@require_permission("system", "manage_sms_config")
async def update_sms_config(
    request: Request,
    config_key: str = Query(..., description="Configuration key"),
    config_value: str = Query(..., description="Configuration value"),
    description: Optional[str] = Query(None, description="Configuration description"),
    db: AsyncSession = Depends(get_db),
):
    """Update SMS Router configuration."""
    try:
        # Check if config exists
        result = await db.execute(
            select(SMSRouterConfig).where(SMSRouterConfig.config_key == config_key)
        )
        existing_config = result.scalar_one_or_none()

        if existing_config:
            # Update existing config
            existing_config.config_value = config_value
            if description:
                existing_config.description = description
            existing_config.updated_at = None  # Will be set by onupdate
        else:
            # Create new config
            new_config = SMSRouterConfig(
                config_key=config_key,
                config_value=config_value,
                description=description,
            )
            db.add(new_config)

        await db.commit()

        return {"message": "Configuration updated successfully", "key": config_key}

    except Exception as e:
        logger.error(f"Error updating SMS config: {e}")
        raise HTTPException(status_code=500, detail="Failed to update configuration")


@router.delete("/phone-mappings/{mapping_id}")
@require_permission("system", "manage_phone_mappings")
async def delete_phone_mapping(
    request: Request, mapping_id: int, db: AsyncSession = Depends(get_db)
):
    """Delete a phone number mapping."""
    try:
        # Get the mapping
        result = await db.execute(
            select(UserPhoneMapping).where(UserPhoneMapping.id == mapping_id)
        )
        mapping = result.scalar_one_or_none()

        if not mapping:
            raise HTTPException(status_code=404, detail="Phone mapping not found")

        # Delete the mapping
        await db.delete(mapping)
        await db.commit()

        return {
            "message": "Phone mapping deleted successfully",
            "mapping_id": mapping_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting phone mapping: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete phone mapping")
