"""Common schemas."""

from pydantic import BaseModel, Field
from typing import Any, Optional
from datetime import datetime


class HealthCheck(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(..., description="Current timestamp")
    version: str = Field(..., description="API version")


class ErrorResponse(BaseModel):
    """Error response."""
    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PaginationParams(BaseModel):
    """Pagination parameters."""
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(10, ge=1, le=100, description="Page size")


class PaginatedResponse(BaseModel):
    """Paginated response."""
    data: list[Any] = Field(..., description="Response data")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")
