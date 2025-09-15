from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.security import HTTPBearer

from apps.fastapi_app.middleware.auth import AuthMiddleware
from apps.fastapi_app.middleware.rate_limiting import RateLimitingMiddleware
from apps.fastapi_app.routes import (
    analytics,
    auth,
    chat,
    mfa,
    oauth,
    rbac,
    sessions,
    sms_router,
    twilio,
    users,
)
from personal_assistant.config.monitoring import monitoring_router
from personal_assistant.config.settings import settings
from personal_assistant.middleware import CorrelationIDMiddleware
from personal_assistant.monitoring import get_metrics_service

# Create security scheme
security = HTTPBearer()

app = FastAPI(
    title="Personal Assistant API",
    description="AI-powered personal assistant API",
    version="0.1.0",
    debug=settings.DEBUG,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add correlation ID middleware (should be early in the chain)
app.add_middleware(CorrelationIDMiddleware)

# Add authentication and rate limiting middleware
app.add_middleware(RateLimitingMiddleware)
app.add_middleware(
    AuthMiddleware,
    exclude_paths=[
        "/",
        "/health",
        "/metrics",  # Exclude metrics endpoint from authentication
        "/docs",
        "/redoc",
        "/openapi.json",
        "/api/v1/auth/login",
        "/api/v1/auth/register",
        "/api/v1/auth/refresh",
        "/api/v1/oauth/callback",  # OAuth callback from external providers
        "/webhook/twilio",  # Keep Twilio webhook accessible
        "/twilio/sms",  # Keep Twilio SMS webhook accessible
        "/sms-router/webhook/sms",  # SMS Router webhook for Twilio
        "/sms-router/webhook/health",  # SMS Router health check
    ],
)

# Include routers
app.include_router(twilio.router)
# Remove the prefix since it's already defined in the router
app.include_router(auth.router)
app.include_router(mfa.router)
app.include_router(sessions.router)
app.include_router(rbac.router)
app.include_router(users.router)
app.include_router(oauth.router)
app.include_router(chat.router)

# Add SMS Router routes
app.include_router(sms_router.router)

# Add Analytics routes
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])

# Include health monitoring router
app.include_router(monitoring_router)

# TODO: Add these routes when they are created
# from .routes import events
# app.include_router(events.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "Personal Assistant API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    try:
        metrics_service = get_metrics_service()
        metrics_data = metrics_service.generate_metrics()
        return Response(
            content=metrics_data, media_type=metrics_service.get_metrics_content_type()
        )
    except Exception as e:
        # Log error but don't expose internal details
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Error generating metrics: {e}")
        return Response(
            content="# Error generating metrics\n",
            media_type="text/plain",
            status_code=500,
        )


if __name__ == "__main__":
    import os

    import uvicorn

    # Use environment variables for host and port, with secure defaults
    host = os.getenv("HOST", "127.0.0.1")  # Default to localhost for security
    port = int(os.getenv("PORT", "8000"))

    uvicorn.run(app, host=host, port=port)
