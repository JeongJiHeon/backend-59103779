"""Calendar event schemas."""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class CalendarEventCreate(BaseModel):
    """Calendar event creation schema."""
    title: str = Field(..., min_length=1, max_length=255, description="Event title")
    description: Optional[str] = Field(None, description="Event description")
    location: Optional[str] = Field(None, max_length=500, description="Event location")
    start_time: datetime = Field(..., description="Event start time")
    end_time: datetime = Field(..., description="Event end time")
    timezone: str = Field(default="UTC", description="Event timezone")
    is_all_day: bool = Field(default=False, description="All day event flag")
    sync_to_google: bool = Field(default=False, description="Sync to Google Calendar")
    
    @field_validator('end_time')
    @classmethod
    def validate_end_time(cls, v, info):
        """Validate end time is after start time."""
        if 'start_time' in info.data and v <= info.data['start_time']:
            raise ValueError('End time must be after start time')
        return v


class CalendarEventUpdate(BaseModel):
    """Calendar event update schema."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    location: Optional[str] = Field(None, max_length=500)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    timezone: Optional[str] = None
    is_all_day: Optional[bool] = None


class CalendarEventResponse(BaseModel):
    """Calendar event response schema."""
    id: str = Field(..., description="Event ID")
    user_id: str = Field(..., description="User ID")
    google_event_id: Optional[str] = Field(None, description="Google event ID")
    title: str = Field(..., description="Event title")
    description: Optional[str] = Field(None, description="Event description")
    location: Optional[str] = Field(None, description="Event location")
    start_time: datetime = Field(..., description="Event start time")
    end_time: datetime = Field(..., description="Event end time")
    timezone: str = Field(..., description="Event timezone")
    is_synced: bool = Field(..., description="Sync status")
    is_all_day: bool = Field(..., description="All day event flag")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    class Config:
        from_attributes = True


class CalendarEventList(BaseModel):
    """Calendar event list response."""
    events: list[CalendarEventResponse] = Field(..., description="List of events")
    total: int = Field(..., description="Total number of events")
