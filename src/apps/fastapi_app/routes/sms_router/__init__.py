"""
SMS Router Service routes for FastAPI.
"""

from fastapi import APIRouter

from .admin import router as admin_router
from .webhooks import router as webhook_router

router = APIRouter(prefix="/sms-router", tags=["sms-router"])

# Include webhook routes
router.include_router(webhook_router, prefix="/webhook")

# Include admin routes
router.include_router(admin_router, prefix="/admin")
