"""Health check endpoints."""

from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.schemas.common import HealthCheck

router = APIRouter()


@router.get(
    "",
    response_model=HealthCheck,
    summary="Health check",
    description="Check if the API is running"
)
async def health_check() -> HealthCheck:
    """
    Health check endpoint.
    
    Returns:
        Health check response
    """
    return HealthCheck(
        status="healthy",
        timestamp=datetime.utcnow(),
        version=settings.APP_VERSION
    )


@router.get(
    "/db",
    response_model=HealthCheck,
    summary="Database health check",
    description="Check if database connection is working"
)
async def database_health_check(db: AsyncSession = Depends(get_db)) -> HealthCheck:
    """
    Database health check endpoint.
    
    Args:
        db: Database session
        
    Returns:
        Health check response
    """
    try:
        # Try to execute a simple query
        await db.execute("SELECT 1")
        return HealthCheck(
            status="healthy",
            timestamp=datetime.utcnow(),
            version=settings.APP_VERSION
        )
    except Exception as e:
        return HealthCheck(
            status=f"unhealthy: {str(e)}",
            timestamp=datetime.utcnow(),
            version=settings.APP_VERSION
        )
