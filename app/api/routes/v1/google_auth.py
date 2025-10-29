"""Google OAuth endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.db.models.user import User
from app.schemas.google_auth import GoogleAuthURL, GoogleConnectionStatus
from app.services.google_calendar_service import GoogleCalendarService

router = APIRouter()


@router.get(
    "/auth-url",
    response_model=GoogleAuthURL,
    summary="Get Google OAuth URL",
    description="Get Google OAuth authorization URL for calendar access"
)
async def get_google_auth_url(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> GoogleAuthURL:
    """
    Get Google OAuth authorization URL.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Authorization URL
    """
    google_service = GoogleCalendarService(db)
    auth_url = google_service.get_authorization_url(state=current_user.id)
    
    return GoogleAuthURL(auth_url=auth_url)


@router.get(
    "/callback",
    summary="Google OAuth callback",
    description="Handle Google OAuth callback"
)
async def google_auth_callback(
    code: str = Query(..., description="Authorization code from Google"),
    state: str = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Handle Google OAuth callback.
    
    Args:
        code: Authorization code from Google
        state: User ID
        db: Database session
        
    Returns:
        Success message
    """
    try:
        google_service = GoogleCalendarService(db)
        flow = google_service.get_oauth_flow(state=state)
        flow.fetch_token(code=code)
        
        credentials = flow.credentials
        await google_service.save_credentials(state, credentials)
        
        return {"message": "Successfully connected to Google Calendar"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to connect to Google Calendar: {str(e)}"
        )


@router.get(
    "/status",
    response_model=GoogleConnectionStatus,
    summary="Get Google connection status",
    description="Check if user is connected to Google Calendar"
)
async def get_google_connection_status(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> GoogleConnectionStatus:
    """
    Get Google connection status.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Connection status
    """
    google_service = GoogleCalendarService(db)
    credentials = await google_service.get_credentials(current_user.id)
    
    return GoogleConnectionStatus(
        is_connected=credentials is not None,
        email=current_user.email if credentials else None
    )


@router.delete(
    "/disconnect",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Disconnect Google Calendar",
    description="Disconnect user's Google Calendar"
)
async def disconnect_google(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Disconnect Google Calendar.
    
    Args:
        current_user: Current authenticated user
        db: Database session
    """
    from sqlalchemy import select, delete
    from app.db.models.google_credential import GoogleCredential
    
    # Delete Google credentials
    await db.execute(
        delete(GoogleCredential).where(
            GoogleCredential.user_id == current_user.id
        )
    )
    
    # Update user's connection status
    current_user.is_google_connected = False
    await db.flush()
