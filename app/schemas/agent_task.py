"""Agent task schemas."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AgentTaskCreate(BaseModel):
    """Agent task creation schema."""
    input_text: str = Field(
        ...,
        min_length=1,
        description="Natural language input for creating calendar event"
    )


class AgentTaskResponse(BaseModel):
    """Agent task response schema."""
    id: str = Field(..., description="Task ID")
    user_id: str = Field(..., description="User ID")
    input_text: str = Field(..., description="Input text")
    status: str = Field(..., description="Task status")
    result: Optional[str] = Field(None, description="Task result (JSON)")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    class Config:
        from_attributes = True


class AgentTaskList(BaseModel):
    """Agent task list response."""
    tasks: list[AgentTaskResponse] = Field(..., description="List of tasks")
    total: int = Field(..., description="Total number of tasks")
