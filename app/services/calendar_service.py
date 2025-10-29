"""Calendar event service."""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from fastapi import HTTPException, status

from app.db.models.calendar_event import CalendarEvent
from app.schemas.calendar_event import CalendarEventCreate, CalendarEventUpdate


class CalendarService:
    """Calendar event service for business logic."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_event(
        self,
        user_id: str,
        event_data: CalendarEventCreate
    ) -> CalendarEvent:
        """
        Create a new calendar event.
        
        Args:
            user_id: User ID
            event_data: Event creation data
            
        Returns:
            Created event
        """
        event = CalendarEvent(
            user_id=user_id,
            title=event_data.title,
            description=event_data.description,
            location=event_data.location,
            start_time=event_data.start_time,
            end_time=event_data.end_time,
            timezone=event_data.timezone,
            is_all_day=event_data.is_all_day,
        )
        
        self.db.add(event)
        await self.db.flush()
        await self.db.refresh(event)
        
        return event
    
    async def get_event_by_id(
        self,
        event_id: str,
        user_id: str
    ) -> Optional[CalendarEvent]:
        """
        Get event by ID.
        
        Args:
            event_id: Event ID
            user_id: User ID
            
        Returns:
            Event or None
        """
        result = await self.db.execute(
            select(CalendarEvent).where(
                and_(
                    CalendarEvent.id == event_id,
                    CalendarEvent.user_id == user_id,
                    CalendarEvent.is_active == True
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_user_events(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[CalendarEvent]:
        """
        Get user's calendar events.
        
        Args:
            user_id: User ID
            start_date: Filter by start date
            end_date: Filter by end date
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of events
        """
        query = select(CalendarEvent).where(
            and_(
                CalendarEvent.user_id == user_id,
                CalendarEvent.is_active == True
            )
        )
        
        if start_date:
            query = query.where(CalendarEvent.start_time >= start_date)
        
        if end_date:
            query = query.where(CalendarEvent.end_time <= end_date)
        
        query = query.offset(skip).limit(limit).order_by(CalendarEvent.start_time)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def update_event(
        self,
        event_id: str,
        user_id: str,
        event_data: CalendarEventUpdate
    ) -> CalendarEvent:
        """
        Update calendar event.
        
        Args:
            event_id: Event ID
            user_id: User ID
            event_data: Event update data
            
        Returns:
            Updated event
            
        Raises:
            HTTPException: If event not found
        """
        event = await self.get_event_by_id(event_id, user_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        
        update_dict = event_data.model_dump(exclude_unset=True)
        
        if update_dict:
            await self.db.execute(
                update(CalendarEvent)
                .where(CalendarEvent.id == event_id)
                .values(**update_dict)
            )
            await self.db.flush()
            await self.db.refresh(event)
        
        return event
    
    async def delete_event(self, event_id: str, user_id: str) -> bool:
        """
        Soft delete calendar event.
        
        Args:
            event_id: Event ID
            user_id: User ID
            
        Returns:
            True if deleted
            
        Raises:
            HTTPException: If event not found
        """
        event = await self.get_event_by_id(event_id, user_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        
        await self.db.execute(
            update(CalendarEvent)
            .where(CalendarEvent.id == event_id)
            .values(is_active=False)
        )
        
        return True
    
    async def count_user_events(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> int:
        """
        Count user's calendar events.
        
        Args:
            user_id: User ID
            start_date: Filter by start date
            end_date: Filter by end date
            
        Returns:
            Number of events
        """
        query = select(CalendarEvent).where(
            and_(
                CalendarEvent.user_id == user_id,
                CalendarEvent.is_active == True
            )
        )
        
        if start_date:
            query = query.where(CalendarEvent.start_time >= start_date)
        
        if end_date:
            query = query.where(CalendarEvent.end_time <= end_date)
        
        result = await self.db.execute(query)
        return len(list(result.scalars().all()))
