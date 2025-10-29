"""AI Agent endpoints."""

from fastapi import APIRouter, Depends, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
import json

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.db.models.user import User
from app.schemas.agent_task import (
    AgentTaskCreate,
    AgentTaskResponse,
    AgentTaskList
)
from app.schemas.calendar_event import CalendarEventCreate, CalendarEventResponse
from app.services.agent_service import AgentService
from app.services.calendar_service import CalendarService

router = APIRouter()


async def process_task_background(task_id: str, db_url: str):
    """Background task to process agent task."""
    from app.db.session import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        agent_service = AgentService(db)
        await agent_service.process_task(task_id)
        await db.commit()


@router.post(
    "/tasks",
    response_model=AgentTaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create agent task",
    description="Create a new AI agent task for natural language event creation"
)
async def create_agent_task(
    task_data: AgentTaskCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> AgentTaskResponse:
    """
    Create agent task.
    
    Args:
        task_data: Task creation data
        background_tasks: Background tasks
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Created task
    """
    from app.core.config import settings
    
    agent_service = AgentService(db)
    task = await agent_service.create_task(current_user.id, task_data)
    
    # Process task in background
    background_tasks.add_task(
        process_task_background,
        task.id,
        settings.DATABASE_URL
    )
    
    return AgentTaskResponse.model_validate(task)


@router.get(
    "/tasks",
    response_model=AgentTaskList,
    summary="List agent tasks",
    description="Get list of AI agent tasks for current user"
)
async def list_agent_tasks(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> AgentTaskList:
    """
    List agent tasks.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List of tasks
    """
    agent_service = AgentService(db)
    tasks = await agent_service.get_user_tasks(current_user.id, skip, limit)
    
    return AgentTaskList(
        tasks=[AgentTaskResponse.model_validate(t) for t in tasks],
        total=len(tasks)
    )


@router.get(
    "/tasks/{task_id}",
    response_model=AgentTaskResponse,
    summary="Get agent task",
    description="Get agent task by ID"
)
async def get_agent_task(
    task_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> AgentTaskResponse:
    """
    Get agent task.
    
    Args:
        task_id: Task ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Task information
    """
    from fastapi import HTTPException
    
    agent_service = AgentService(db)
    task = await agent_service.get_task_by_id(task_id, current_user.id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return AgentTaskResponse.model_validate(task)


@router.post(
    "/tasks/{task_id}/create-event",
    response_model=CalendarEventResponse,
    summary="Create event from task",
    description="Create calendar event from completed agent task"
)
async def create_event_from_task(
    task_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> CalendarEventResponse:
    """
    Create calendar event from agent task.
    
    Args:
        task_id: Task ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Created event
    """
    from fastapi import HTTPException
    from app.db.models.agent_task import TaskStatus
    from datetime import datetime
    
    agent_service = AgentService(db)
    task = await agent_service.get_task_by_id(task_id, current_user.id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    if task.status != TaskStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task is not completed yet"
        )
    
    # Parse task result
    try:
        event_data_dict = json.loads(task.result)
        
        # Convert to CalendarEventCreate
        event_data = CalendarEventCreate(
            title=event_data_dict["title"],
            description=event_data_dict.get("description"),
            location=event_data_dict.get("location"),
            start_time=datetime.fromisoformat(event_data_dict["start_time"]),
            end_time=datetime.fromisoformat(event_data_dict["end_time"]),
            timezone=event_data_dict.get("timezone", "UTC"),
            is_all_day=event_data_dict.get("is_all_day", False),
            sync_to_google=False
        )
        
        calendar_service = CalendarService(db)
        event = await calendar_service.create_event(current_user.id, event_data)
        
        return CalendarEventResponse.model_validate(event)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create event from task: {str(e)}"
        )
