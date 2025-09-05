"""
OAuth Routes

This module provides OAuth-related API endpoints for initiating OAuth flows,
handling callbacks, and managing OAuth integrations.
"""

from typing import AsyncGenerator, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from personal_assistant.database.models.users import User
from personal_assistant.database.session import AsyncSessionLocal
from personal_assistant.oauth.exceptions import OAuthError, OAuthProviderError
from personal_assistant.oauth.oauth_manager import OAuthManager

# Create router with security
security = HTTPBearer()
router = APIRouter(prefix="/api/v1/oauth", tags=["oauth"])

# Pydantic models for request/response


class OAuthInitiateRequest(BaseModel):
    provider: str
    scopes: List[str]
    redirect_uri: Optional[str] = None


class OAuthInitiateResponse(BaseModel):
    authorization_url: str
    state_token: str
    provider: str
    scopes: List[str]


class OAuthCallbackRequest(BaseModel):
    state: str
    code: str
    provider: str


class OAuthCallbackResponse(BaseModel):
    integration_id: int
    provider: str
    status: str
    scopes: List[str]


class OAuthIntegrationResponse(BaseModel):
    id: int
    provider: str
    status: str
    is_active: bool
    scopes: List[str]
    created_at: str
    last_sync_at: Optional[str] = None
    metadata: Optional[dict] = None


class OAuthProviderInfo(BaseModel):
    name: str
    display_name: str
    description: str
    scopes: List[dict]


# Dependencies


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    from personal_assistant.database.session import _get_session_factory

    session = _get_session_factory()()
    try:
        yield session
    finally:
        await session.close()


async def get_current_user(request: Request) -> User:
    """
    Get current authenticated user.

    This dependency is already handled by the existing auth middleware,
    but we include it here for clarity and type hints.
    """
    # The actual user extraction is handled by the auth middleware
    # This is just for type hints and documentation
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required"
        )

    # In a real implementation, you would fetch the user from the database
    # For now, we'll create a minimal user object
    user = User()
    user.id = user_id
    return user


async def get_oauth_manager() -> OAuthManager:
    """Get OAuth manager instance."""
    return OAuthManager()


# Routes


@router.get(
    "/providers",
    response_model=List[OAuthProviderInfo],
    dependencies=[Depends(security)],
)
async def get_supported_providers(
    oauth_manager: OAuthManager = Depends(get_oauth_manager),
):
    """
    Get list of supported OAuth providers with their available scopes.
    """
    try:
        providers = []
        for provider_name in oauth_manager.get_supported_providers():
            scopes = oauth_manager.get_provider_scopes(provider_name)

            # Get provider display information
            provider_info = {
                "google": {
                    "display_name": "Google",
                    "description": "Google services including Calendar, Drive, and Gmail",
                },
                "microsoft": {
                    "display_name": "Microsoft",
                    "description": "Microsoft 365 services including Outlook and OneDrive",
                },
                "notion": {
                    "display_name": "Notion",
                    "description": "Notion workspace and pages",
                },
                "youtube": {
                    "display_name": "YouTube",
                    "description": "YouTube videos and channels",
                },
            }.get(
                provider_name,
                {
                    "display_name": provider_name.title(),
                    "description": f"{provider_name.title()} integration",
                },
            )

            providers.append(
                OAuthProviderInfo(
                    name=provider_name,
                    display_name=provider_info["display_name"],
                    description=provider_info["description"],
                    scopes=scopes,
                )
            )

        return providers

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get providers: {str(e)}",
        )


@router.post(
    "/initiate", response_model=OAuthInitiateResponse, dependencies=[Depends(security)]
)
async def initiate_oauth_flow(
    request: OAuthInitiateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    oauth_manager: OAuthManager = Depends(get_oauth_manager),
):
    """
    Initiate an OAuth flow for a user.
    """
    try:
        # Validate provider
        if request.provider not in oauth_manager.get_supported_providers():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported provider: {request.provider}",
            )

        # Initiate OAuth flow
        result = await oauth_manager.initiate_oauth_flow(
            db=db,
            user_id=int(current_user.id),
            provider_name=request.provider,
            scopes=request.scopes,
            redirect_uri=request.redirect_uri,
        )

        return OAuthInitiateResponse(**result)

    except OAuthError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except OAuthProviderError as e:
        # Handle missing OAuth credentials gracefully
        if "OAuth credentials not configured" in str(e):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"OAuth service temporarily unavailable: {str(e)}. Please contact your administrator.",
            )
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate OAuth flow: {str(e)}",
        )


@router.get("/callback")
async def oauth_callback(
    state: str = Query(..., description="OAuth state parameter"),
    code: str = Query(..., description="OAuth authorization code"),
    provider: Optional[str] = Query(
        None,
        description="OAuth provider name (optional, will be extracted from state if not provided)",
    ),
    db: AsyncSession = Depends(get_db),
    oauth_manager: OAuthManager = Depends(get_oauth_manager),
):
    """
    Handle OAuth callback and complete the flow.

    This endpoint is called by the OAuth provider after user authorization.
    """
    try:
        # If provider is not provided, extract it from the state token
        if not provider:
            # Get the state from database to extract provider without validation
            state_obj = await oauth_manager.security_service.get_state_by_token(
                db=db, state_token=state
            )
            if not state_obj:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid state token",
                )
            provider = state_obj.provider

        # Handle OAuth callback
        result = await oauth_manager.handle_oauth_callback(
            db=db, state_token=state, authorization_code=code, provider_name=provider
        )

        # In a real implementation, you might want to redirect the user
        # to a success page or return a success response
        return {
            "message": "OAuth integration completed successfully",
            "integration_id": result["integration_id"],
            "provider": result["provider"],
            "status": result["status"],
        }

    except OAuthError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete OAuth flow: {str(e)}",
        )


@router.get(
    "/integrations",
    response_model=List[OAuthIntegrationResponse],
    dependencies=[Depends(security)],
)
async def get_user_integrations(
    provider: Optional[str] = Query(None, description="Filter by provider"),
    active_only: bool = Query(True, description="Return only active integrations"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    oauth_manager: OAuthManager = Depends(get_oauth_manager),
):
    """
    Get OAuth integrations for the current user.
    """
    try:
        integrations = await oauth_manager.get_user_integrations(
            db=db,
            user_id=int(current_user.id),
            provider=provider,
            active_only=active_only,
        )

        return [OAuthIntegrationResponse(**integration) for integration in integrations]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get integrations: {str(e)}",
        )


@router.post("/integrations/{integration_id}/refresh", dependencies=[Depends(security)])
async def refresh_integration_tokens(
    integration_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    oauth_manager: OAuthManager = Depends(get_oauth_manager),
):
    """
    Refresh tokens for an OAuth integration.
    """
    print(f"🔍 ROUTE DEBUG: Starting refresh for integration {integration_id}")

    try:
        print(f"🔍 ROUTE DEBUG: Calling oauth_manager.refresh_integration_tokens")
        success = await oauth_manager.refresh_integration_tokens(
            db=db, integration_id=integration_id
        )

        print(
            f"🔍 ROUTE DEBUG: oauth_manager returned: {success} (type: {type(success)})"
        )

        if success:
            print(f"🔍 ROUTE DEBUG: Success case - returning 200")
            return {"message": "Tokens refreshed successfully"}
        else:
            print(f"🔍 ROUTE DEBUG: Failure case - raising 400 error")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to refresh tokens",
            )

    except OAuthProviderError as e:
        print(f"🔍 ROUTE DEBUG: Caught OAuthProviderError: {e}")
        # Handle missing OAuth credentials gracefully
        if "OAuth credentials not configured" in str(e):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"OAuth service temporarily unavailable: {str(e)}. Please contact your administrator.",
            )
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException as e:
        print(f"🔍 ROUTE DEBUG: Caught HTTPException: {e.status_code} - {e.detail}")
        raise
    except Exception as e:
        print(f"🔍 ROUTE DEBUG: Caught unexpected Exception: {e}")
        print(f"🔍 ROUTE DEBUG: Exception type: {type(e)}")
        import traceback

        print(f"🔍 ROUTE DEBUG: Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to refresh tokens: {str(e)}",
        )


@router.delete("/integrations/{integration_id}", dependencies=[Depends(security)])
async def revoke_integration(
    integration_id: int,
    reason: Optional[str] = Query(None, description="Reason for revocation"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    oauth_manager: OAuthManager = Depends(get_oauth_manager),
):
    """
    Revoke an OAuth integration.
    """
    try:
        success = await oauth_manager.revoke_integration(
            db=db, integration_id=integration_id, reason=reason
        )

        if success:
            return {"message": "Integration revoked successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to revoke integration",
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to revoke integration: {str(e)}",
        )


@router.post("/integrations/sync", dependencies=[Depends(security)])
async def sync_integrations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    oauth_manager: OAuthManager = Depends(get_oauth_manager),
):
    """
    Sync all OAuth integrations for the current user.
    """
    try:
        sync_results = await oauth_manager.sync_all_integrations(
            db=db, user_id=int(current_user.id)
        )

        return {"message": "Integration sync completed", "results": sync_results}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync integrations: {str(e)}",
        )


@router.get("/status", dependencies=[Depends(security)])
async def get_oauth_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    oauth_manager: OAuthManager = Depends(get_oauth_manager),
):
    """
    Get OAuth status summary for the current user.
    """
    try:
        # Get integration status
        from personal_assistant.oauth.services.integration_service import (
            OAuthIntegrationService,
        )

        integration_service = OAuthIntegrationService()
        status_summary = await integration_service.get_integration_status(
            db=db, user_id=int(current_user.id)
        )

        # Get consent summary
        from personal_assistant.oauth.services.consent_service import (
            OAuthConsentService,
        )

        consent_service = OAuthConsentService()
        consent_summary = await consent_service.get_consent_summary(
            db=db, user_id=int(current_user.id)
        )

        return {"integrations": status_summary, "consents": consent_summary}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get OAuth status: {str(e)}",
        )
