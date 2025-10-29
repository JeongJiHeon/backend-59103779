"""Authentication endpoints."""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.db.session import get_db
from app.schemas.user import UserCreate, UserLogin, TokenResponse, RefreshTokenRequest
from app.services.user_service import UserService

router = APIRouter()


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Register a new user account and return access token"
)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """
    Register new user.
    
    Args:
        user_data: User registration data
        db: Database session
        
    Returns:
        Access and refresh tokens
    """
    user_service = UserService(db)
    user = await user_service.create_user(user_data)
    
    # Create tokens
    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_refresh_token(
        data={"sub": user.id},
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login",
    description="Login with email and password"
)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """
    Login user.
    
    Args:
        credentials: Login credentials
        db: Database session
        
    Returns:
        Access and refresh tokens
        
    Raises:
        HTTPException: If credentials are invalid
    """
    user_service = UserService(db)
    user = await user_service.authenticate_user(
        credentials.email,
        credentials.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create tokens
    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_refresh_token(
        data={"sub": user.id},
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh token",
    description="Get new access token using refresh token"
)
async def refresh_token(
    token_data: RefreshTokenRequest
) -> TokenResponse:
    """
    Refresh access token.
    
    Args:
        token_data: Refresh token
        
    Returns:
        New access token
        
    Raises:
        HTTPException: If refresh token is invalid
    """
    try:
        payload = decode_token(token_data.refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Create new access token
        access_token = create_access_token(
            data={"sub": user_id},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=token_data.refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
