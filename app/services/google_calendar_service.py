"""Google Calendar integration service."""

from typing import Optional, Dict, Any
from datetime import datetime
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.db.models.google_credential import GoogleCredential
from app.db.models.user import User


class GoogleCalendarService:
    """Google Calendar integration service."""
    
    SCOPES = [
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/calendar.events'
    ]
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    def get_oauth_flow(self, state: Optional[str] = None) -> Flow:
        """
        Create OAuth flow for Google Calendar.
        
        Args:
            state: Optional state parameter
            
        Returns:
            OAuth flow object
        """
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
                }
            },
            scopes=self.SCOPES,
            state=state
        )
        flow.redirect_uri = settings.GOOGLE_REDIRECT_URI
        return flow
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """
        Get Google OAuth authorization URL.
        
        Args:
            state: Optional state parameter
            
        Returns:
            Authorization URL
        """
        flow = self.get_oauth_flow(state)
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        return auth_url
    
    async def save_credentials(
        self,
        user_id: str,
        credentials: Credentials
    ) -> GoogleCredential:
        """
        Save Google credentials to database.
        
        Args:
            user_id: User ID
            credentials: Google OAuth credentials
            
        Returns:
            Saved credential record
        """
        # Check if credentials already exist
        result = await self.db.execute(
            select(GoogleCredential).where(GoogleCredential.user_id == user_id)
        )
        existing_cred = result.scalar_one_or_none()
        
        cred_data = {
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": json.dumps(credentials.scopes) if credentials.scopes else None,
            "expiry": credentials.expiry,
        }
        
        if existing_cred:
            # Update existing credentials
            for key, value in cred_data.items():
                setattr(existing_cred, key, value)
            credential = existing_cred
        else:
            # Create new credentials
            credential = GoogleCredential(user_id=user_id, **cred_data)
            self.db.add(credential)
        
        await self.db.flush()
        await self.db.refresh(credential)
        
        # Update user's Google connection status
        await self.db.execute(
            select(User).where(User.id == user_id)
        )
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if user:
            user.is_google_connected = True
            await self.db.flush()
        
        return credential
    
    async def get_credentials(self, user_id: str) -> Optional[Credentials]:
        """
        Get Google credentials for user.
        
        Args:
            user_id: User ID
            
        Returns:
            Google credentials or None
        """
        result = await self.db.execute(
            select(GoogleCredential).where(GoogleCredential.user_id == user_id)
        )
        cred_record = result.scalar_one_or_none()
        
        if not cred_record:
            return None
        
        credentials = Credentials(
            token=cred_record.access_token,
            refresh_token=cred_record.refresh_token,
            token_uri=cred_record.token_uri,
            client_id=cred_record.client_id,
            client_secret=cred_record.client_secret,
            scopes=json.loads(cred_record.scopes) if cred_record.scopes else None,
        )
        
        return credentials
    
    async def create_calendar_event(
        self,
        user_id: str,
        event_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create event in Google Calendar.
        
        Args:
            user_id: User ID
            event_data: Event data
            
        Returns:
            Created event from Google Calendar
        """
        credentials = await self.get_credentials(user_id)
        if not credentials:
            raise ValueError("Google credentials not found")
        
        service = build('calendar', 'v3', credentials=credentials)
        
        event = service.events().insert(
            calendarId='primary',
            body=event_data
        ).execute()
        
        return event
    
    async def update_calendar_event(
        self,
        user_id: str,
        event_id: str,
        event_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update event in Google Calendar.
        
        Args:
            user_id: User ID
            event_id: Google Calendar event ID
            event_data: Updated event data
            
        Returns:
            Updated event from Google Calendar
        """
        credentials = await self.get_credentials(user_id)
        if not credentials:
            raise ValueError("Google credentials not found")
        
        service = build('calendar', 'v3', credentials=credentials)
        
        event = service.events().update(
            calendarId='primary',
            eventId=event_id,
            body=event_data
        ).execute()
        
        return event
    
    async def delete_calendar_event(
        self,
        user_id: str,
        event_id: str
    ) -> None:
        """
        Delete event from Google Calendar.
        
        Args:
            user_id: User ID
            event_id: Google Calendar event ID
        """
        credentials = await self.get_credentials(user_id)
        if not credentials:
            raise ValueError("Google credentials not found")
        
        service = build('calendar', 'v3', credentials=credentials)
        
        service.events().delete(
            calendarId='primary',
            eventId=event_id
        ).execute()
