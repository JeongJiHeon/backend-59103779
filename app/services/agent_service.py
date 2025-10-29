"""AI Agent service for natural language calendar event creation."""

import re
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.db.models.agent_task import AgentTask, TaskStatus
from app.schemas.agent_task import AgentTaskCreate


class AgentService:
    """AI Agent service for processing natural language inputs."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_task(
        self,
        user_id: str,
        task_data: AgentTaskCreate
    ) -> AgentTask:
        """
        Create a new agent task.
        
        Args:
            user_id: User ID
            task_data: Task creation data
            
        Returns:
            Created task
        """
        task = AgentTask(
            user_id=user_id,
            input_text=task_data.input_text,
            status=TaskStatus.PENDING
        )
        
        self.db.add(task)
        await self.db.flush()
        await self.db.refresh(task)
        
        return task
    
    async def process_task(self, task_id: str) -> AgentTask:
        """
        Process agent task to extract calendar event information.
        
        Args:
            task_id: Task ID
            
        Returns:
            Processed task
        """
        result = await self.db.execute(
            select(AgentTask).where(AgentTask.id == task_id)
        )
        task = result.scalar_one_or_none()
        
        if not task:
            raise ValueError("Task not found")
        
        # Update status to processing
        task.status = TaskStatus.PROCESSING
        await self.db.flush()
        
        try:
            # Parse natural language input
            event_data = self._parse_natural_language(task.input_text)
            
            # Save result
            task.result = json.dumps(event_data)
            task.status = TaskStatus.COMPLETED
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
        
        await self.db.flush()
        await self.db.refresh(task)
        
        return task
    
    def _parse_natural_language(self, text: str) -> Dict[str, Any]:
        """
        Parse natural language text to extract event information.
        This is a simplified implementation. In production, you would use
        an LLM or NLP library for better accuracy.
        
        Args:
            text: Natural language input
            
        Returns:
            Parsed event data
        """
        text_lower = text.lower()
        
        # Extract title (simple heuristic)
        title = self._extract_title(text)
        
        # Extract date and time
        start_time, end_time = self._extract_datetime(text_lower)
        
        # Extract location
        location = self._extract_location(text)
        
        # Extract description
        description = text
        
        return {
            "title": title,
            "description": description,
            "location": location,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "timezone": "UTC",
            "is_all_day": False
        }
    
    def _extract_title(self, text: str) -> str:
        """Extract title from text."""
        # Simple heuristic: first sentence or first 50 characters
        sentences = text.split('.')
        if sentences:
            title = sentences[0].strip()
            return title[:100] if len(title) > 100 else title
        return text[:50]
    
    def _extract_datetime(self, text: str) -> tuple[datetime, datetime]:
        """
        Extract date and time from text.
        This is a simplified implementation.
        """
        now = datetime.utcnow()
        
        # Look for common time patterns
        time_patterns = {
            r'tomorrow': timedelta(days=1),
            r'next week': timedelta(weeks=1),
            r'next month': timedelta(days=30),
        }
        
        start_time = now + timedelta(days=1)  # Default to tomorrow
        
        for pattern, delta in time_patterns.items():
            if re.search(pattern, text):
                start_time = now + delta
                break
        
        # Look for time (e.g., "at 3pm", "at 14:00")
        time_match = re.search(r'at (\d{1,2}):?(\d{2})?\s*(am|pm)?', text)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2)) if time_match.group(2) else 0
            period = time_match.group(3)
            
            if period == 'pm' and hour < 12:
                hour += 12
            elif period == 'am' and hour == 12:
                hour = 0
            
            start_time = start_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
        else:
            # Default to 9 AM
            start_time = start_time.replace(hour=9, minute=0, second=0, microsecond=0)
        
        # Default duration: 1 hour
        end_time = start_time + timedelta(hours=1)
        
        return start_time, end_time
    
    def _extract_location(self, text: str) -> Optional[str]:
        """Extract location from text."""
        # Look for common location patterns
        location_patterns = [
            r'at ([\w\s]+)',
            r'in ([\w\s]+)',
            r'location: ([\w\s]+)',
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                # Filter out common non-location words
                if location.lower() not in ['the', 'my', 'our', 'their']:
                    return location[:100]
        
        return None
    
    async def get_task_by_id(self, task_id: str, user_id: str) -> Optional[AgentTask]:
        """
        Get task by ID.
        
        Args:
            task_id: Task ID
            user_id: User ID
            
        Returns:
            Task or None
        """
        result = await self.db.execute(
            select(AgentTask).where(
                AgentTask.id == task_id,
                AgentTask.user_id == user_id
            )
        )
        return result.scalar_one_or_none()
    
    async def get_user_tasks(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> list[AgentTask]:
        """
        Get user's agent tasks.
        
        Args:
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of tasks
        """
        result = await self.db.execute(
            select(AgentTask)
            .where(AgentTask.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(AgentTask.created_at.desc())
        )
        return list(result.scalars().all())
