"""Create admin user."""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.services.user_service import UserService
from app.schemas.user import UserCreate


async def create_admin_user():
    """Create admin user."""
    async with AsyncSessionLocal() as db:
        user_service = UserService(db)
        
        admin_data = UserCreate(
            email="admin@example.com",
            name="Admin User",
            password="AdminPass123"
        )
        
        try:
            user = await user_service.create_user(admin_data)
            await db.commit()
            print(f"Admin user created successfully!")
            print(f"Email: {user.email}")
            print(f"ID: {user.id}")
        except Exception as e:
            print(f"Error creating admin user: {e}")


if __name__ == "__main__":
    asyncio.run(create_admin_user())
