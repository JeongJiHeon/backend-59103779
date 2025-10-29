"""Health check endpoint tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.unit
async def test_health_check(client: AsyncClient):
    """Test health check endpoint."""
    response = await client.get("/api/v1/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data


@pytest.mark.integration
async def test_database_health_check(client: AsyncClient):
    """Test database health check endpoint."""
    response = await client.get("/api/v1/health/db")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data
