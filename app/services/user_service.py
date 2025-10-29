"""User service."""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from fastapi import HTTPException, status

from app.db.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


class UserService:
    """User service for business logic."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user.
        
        Args:
            user_data: User creation data
            
        Returns:
            Created user
            
        Raises:
            HTTPException: If user already exists
        """
        # Check if user already exists
        existing_user = await self.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists"
            )
        
        # Create user
        user = User(
            email=user_data.email,
            name=user_data.name,
            password_hash=get_password_hash(user_data.password)
        )
        
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        
        return user
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User or None
        """
        result = await self.db.execute(
            select(User).where(User.id == user_id, User.is_active == True)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email.
        
        Args:
            email: User email
            
        Returns:
            User or None
        """
        result = await self.db.execute(
            select(User).where(User.email == email, User.is_active == True)
        )
        return result.scalar_one_or_none()
    
    async def update_user(self, user_id: str, user_data: UserUpdate) -> User:
        """
        Update user.
        
        Args:
            user_id: User ID
            user_data: User update data
            
        Returns:
            Updated user
            
        Raises:
            HTTPException: If user not found
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        update_dict = user_data.model_dump(exclude_unset=True)
        
        # Hash password if provided
        if "password" in update_dict:
            update_dict["password_hash"] = get_password_hash(update_dict.pop("password"))
        
        if update_dict:
            await self.db.execute(
                update(User)
                .where(User.id == user_id)
                .values(**update_dict)
            )
            await self.db.flush()
            await self.db.refresh(user)
        
        return user
    
    async def delete_user(self, user_id: str) -> bool:
        """
        Soft delete user.
        
        Args:
            user_id: User ID
            
        Returns:
            True if deleted
            
        Raises:
            HTTPException: If user not found
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(is_active=False)
        )
        
        return True
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate user.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            User if authenticated, None otherwise
        """
        user = await self.get_user_by_email(email)
        
        if not user or not user.password_hash:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        return user
