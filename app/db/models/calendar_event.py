"""Calendar event model."""

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.db.base import BaseModel


class CalendarEvent(BaseModel):
    """Calendar event model."""
    
    __tablename__ = "calendar_events"
    
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    google_event_id = Column(String(255), nullable=True, index=True)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String(500), nullable=True)
    
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    timezone = Column(String(50), default="UTC")
    
    is_synced = Column(Boolean, default=False)
    is_all_day = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="calendar_events")
    
    def __repr__(self):
        return f"<CalendarEvent(id={self.id}, title={self.title})>"
