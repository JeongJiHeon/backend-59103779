"""Calendar event endpoints."""

from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.db.models.user import User
from app.schemas.calendar_event import (
    CalendarEventCreate,
    CalendarEventUpdate,
    CalendarEventResponse,
    CalendarEventList
)
from app.services.calendar_service import CalendarService
from app.services.google_calendar_service import GoogleCalendarService

router = APIRouter()


@router.post(
    "",
    response_model=CalendarEventResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create calendar event",
    description="Create a new calendar event"
)
async def create_event(
    event_data: CalendarEventCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> CalendarEventResponse:
    """
    Create calendar event.
    
    Args:
        event_data: Event creation data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Created event
    """
    calendar_service = CalendarService(db)
    event = await calendar_service.create_event(current_user.id, event_data)
    
    # Sync to Google Calendar if requested
    if event_data.sync_to_google and current_user.is_google_connected:
        try:
            google_service = GoogleCalendarService(db)
            google_event_data = {
                'summary': event.title,
                'description': event.description,
                'location': event.location,
                'start': {
                    'dateTime': event.start_time.isoformat(),
                    'timeZone': event.timezone,
                },
                'end': {
                    'dateTime': event.end_time.isoformat(),
                    'timeZone': event.timezone,
                },
            }
            google_event = await google_service.create_calendar_event(
                current_user.id,
                google_event_data
            )
            event.google_event_id = google_event.get('id')
            event.is_synced = True
            await db.flush()
        except Exception as e:
            # Log error but don't fail the request
            pass
    
    return CalendarEventResponse.model_validate(event)


@router.get(
    "",
    response_model=CalendarEventList,
    summary="List calendar events",
    description="Get list of calendar events for current user"
)
async def list_events(
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> CalendarEventList:
    """
    List calendar events.
    
    Args:
        start_date: Filter by start date
        end_date: Filter by end date
        skip: Number of records to skip
        limit: Maximum number of records
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List of events
    """
    calendar_service = CalendarService(db)
    events = await calendar_service.get_user_events(
        current_user.id,
        start_date,
        end_date,
        skip,
        limit
    )
    total = await calendar_service.count_user_events(
        current_user.id,
        start_date,
        end_date
    )
    
    return CalendarEventList(
        events=[CalendarEventResponse.model_validate(e) for e in events],
        total=total
    )


@router.get(
    "/{event_id}",
    response_model=CalendarEventResponse,
    summary="Get calendar event",
    description="Get calendar event by ID"
)
async def get_event(
    event_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> CalendarEventResponse:
    """
    Get calendar event.
    
    Args:
        event_id: Event ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Event information
    """
    calendar_service = CalendarService(db)
    event = await calendar_service.get_event_by_id(event_id, current_user.id)
    
    if not event:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    return CalendarEventResponse.model_validate(event)


@router.put(
    "/{event_id}",
    response_model=CalendarEventResponse,
    summary="Update calendar event",
    description="Update calendar event by ID"
)
async def update_event(
    event_id: str,
    event_data: CalendarEventUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> CalendarEventResponse:
    """
    Update calendar event.
    
    Args:
        event_id: Event ID
        event_data: Event update data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Updated event
    """
    calendar_service = CalendarService(db)
    event = await calendar_service.update_event(event_id, current_user.id, event_data)
    
    return CalendarEventResponse.model_validate(event)


@router.delete(
    "/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete calendar event",
    description="Delete calendar event by ID"
)
async def delete_event(
    event_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Delete calendar event.
    
    Args:
        event_id: Event ID
        current_user: Current authenticated user
        db: Database session
    """
    calendar_service = CalendarService(db)
    await calendar_service.delete_event(event_id, current_user.id)
