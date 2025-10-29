"""User model."""

from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship

from app.db.base import BaseModel


class User(BaseModel):
    """User model."""
    
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=True)  # Nullable for OAuth users
    is_google_connected = Column(Boolean, default=False)
    
    # Relationships
    calendar_events = relationship(
        "CalendarEvent",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    google_credential = relationship(
        "GoogleCredential",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    agent_tasks = relationship(
        "AgentTask",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"
