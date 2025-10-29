"""Initialize database with initial data."""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
from app.db.base import Base
from app.db.models import *  # noqa: F401, F403


async def init_db():
    """Initialize database."""
    print("Creating database tables...")
    
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=True,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    await engine.dispose()
    
    print("Database tables created successfully!")


if __name__ == "__main__":
    asyncio.run(init_db())
