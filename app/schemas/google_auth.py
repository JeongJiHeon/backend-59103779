"""Google authentication schemas."""

from pydantic import BaseModel, Field
from typing import Optional


class GoogleAuthURL(BaseModel):
    """Google auth URL response."""
    auth_url: str = Field(..., description="Google OAuth authorization URL")


class GoogleAuthCallback(BaseModel):
    """Google auth callback schema."""
    code: str = Field(..., description="Authorization code from Google")
    state: Optional[str] = Field(None, description="State parameter")


class GoogleConnectionStatus(BaseModel):
    """Google connection status."""
    is_connected: bool = Field(..., description="Connection status")
    email: Optional[str] = Field(None, description="Connected Google account email")
