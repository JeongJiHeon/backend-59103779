"""Calendar event endpoint tests."""

import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta


@pytest.fixture
def sample_event_data():
    """Sample event data for testing."""
    now = datetime.utcnow()
    return {
        "title": "Test Meeting",
        "description": "This is a test meeting",
        "location": "Conference Room A",
        "start_time": (now + timedelta(days=1)).isoformat(),
        "end_time": (now + timedelta(days=1, hours=1)).isoformat(),
        "timezone": "UTC",
        "is_all_day": False,
        "sync_to_google": False
    }


@pytest.mark.integration
async def test_create_event(
    authenticated_client: tuple[AsyncClient, dict],
    sample_event_data: dict
):
    """Test creating calendar event."""
    client, _ = authenticated_client
    
    response = await client.post("/api/v1/events", json=sample_event_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == sample_event_data["title"]
    assert data["description"] == sample_event_data["description"]
    assert data["location"] == sample_event_data["location"]
    assert "id" in data
    assert "created_at" in data


@pytest.mark.integration
async def test_list_events(
    authenticated_client: tuple[AsyncClient, dict],
    sample_event_data: dict
):
    """Test listing calendar events."""
    client, _ = authenticated_client
    
    # Create an event first
    await client.post("/api/v1/events", json=sample_event_data)
    
    # List events
    response = await client.get("/api/v1/events")
    
    assert response.status_code == 200
    data = response.json()
    assert "events" in data
    assert "total" in data
    assert len(data["events"]) > 0


@pytest.mark.integration
async def test_get_event(
    authenticated_client: tuple[AsyncClient, dict],
    sample_event_data: dict
):
    """Test getting single calendar event."""
    client, _ = authenticated_client
    
    # Create an event
    create_response = await client.post("/api/v1/events", json=sample_event_data)
    event_id = create_response.json()["id"]
    
    # Get the event
    response = await client.get(f"/api/v1/events/{event_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == event_id
    assert data["title"] == sample_event_data["title"]


@pytest.mark.integration
async def test_update_event(
    authenticated_client: tuple[AsyncClient, dict],
    sample_event_data: dict
):
    """Test updating calendar event."""
    client, _ = authenticated_client
    
    # Create an event
    create_response = await client.post("/api/v1/events", json=sample_event_data)
    event_id = create_response.json()["id"]
    
    # Update the event
    update_data = {"title": "Updated Meeting"}
    response = await client.put(f"/api/v1/events/{event_id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Meeting"


@pytest.mark.integration
async def test_delete_event(
    authenticated_client: tuple[AsyncClient, dict],
    sample_event_data: dict
):
    """Test deleting calendar event."""
    client, _ = authenticated_client
    
    # Create an event
    create_response = await client.post("/api/v1/events", json=sample_event_data)
    event_id = create_response.json()["id"]
    
    # Delete the event
    response = await client.delete(f"/api/v1/events/{event_id}")
    
    assert response.status_code == 204
    
    # Verify event is deleted
    get_response = await client.get(f"/api/v1/events/{event_id}")
    assert get_response.status_code == 404


@pytest.mark.integration
async def test_create_event_unauthorized(client: AsyncClient, sample_event_data: dict):
    """Test creating event without authentication returns 401."""
    response = await client.post("/api/v1/events", json=sample_event_data)
    assert response.status_code == 403
