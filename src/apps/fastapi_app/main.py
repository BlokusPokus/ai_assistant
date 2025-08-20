from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from personal_assistant.config.settings import settings

from apps.fastapi_app.middleware.auth import AuthMiddleware
from apps.fastapi_app.middleware.rate_limiting import RateLimitingMiddleware
from apps.fastapi_app.routes import twilio, auth, mfa, sessions, rbac
from personal_assistant.config.monitoring import monitoring_router

app = FastAPI(
    title="Personal Assistant API",
    description="AI-powered personal assistant API",
    version="0.1.0",
    debug=settings.DEBUG
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add authentication and rate limiting middleware
app.add_middleware(RateLimitingMiddleware)
app.add_middleware(AuthMiddleware)

# Include routers
app.include_router(twilio.router)
# Remove the prefix since it's already defined in the router
app.include_router(auth.router)
app.include_router(mfa.router)
app.include_router(sessions.router)
app.include_router(rbac.router)

# Include health monitoring router
app.include_router(monitoring_router)

# TODO: Add these routes when they are created
# from .routes import events, users
# app.include_router(events.router, prefix="/api/v1")
# app.include_router(users.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "Personal Assistant API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
