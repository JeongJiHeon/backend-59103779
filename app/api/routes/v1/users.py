"""User management endpoints."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.db.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter()


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get currently authenticated user information"
)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
) -> UserResponse:
    """
    Get current user information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User information
    """
    return UserResponse.model_validate(current_user)


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update current user",
    description="Update currently authenticated user information"
)
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Update current user.
    
    Args:
        user_data: User update data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Updated user information
    """
    user_service = UserService(db)
    updated_user = await user_service.update_user(current_user.id, user_data)
    return UserResponse.model_validate(updated_user)


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete current user",
    description="Delete currently authenticated user account"
)
async def delete_current_user(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Delete current user.
    
    Args:
        current_user: Current authenticated user
        db: Database session
    """
    user_service = UserService(db)
    await user_service.delete_user(current_user.id)
