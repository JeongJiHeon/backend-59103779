"""Agent task model for AI-generated calendar events."""

from sqlalchemy import Column, String, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.db.base import BaseModel


class TaskStatus(str, enum.Enum):
    """Task status enum."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentTask(BaseModel):
    """Agent task model for AI-generated calendar events."""
    
    __tablename__ = "agent_tasks"
    
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    input_text = Column(Text, nullable=False)
    status = Column(
        SQLEnum(TaskStatus),
        default=TaskStatus.PENDING,
        nullable=False
    )
    
    result = Column(Text, nullable=True)  # JSON result
    error_message = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="agent_tasks")
    
    def __repr__(self):
        return f"<AgentTask(id={self.id}, status={self.status})>"
