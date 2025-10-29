"""API v1 routes."""

from fastapi import APIRouter

from app.api.routes.v1 import health, auth, users, calendar_events, google_auth, agent

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(calendar_events.router, prefix="/events", tags=["calendar-events"])
api_router.include_router(google_auth.router, prefix="/google", tags=["google-auth"])
api_router.include_router(agent.router, prefix="/agent", tags=["agent"])
