"""Authentication endpoint tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.integration
async def test_register_user(client: AsyncClient, sample_user_data: dict):
    """Test user registration."""
    response = await client.post("/api/v1/auth/register", json=sample_user_data)
    
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert "expires_in" in data


@pytest.mark.integration
async def test_register_duplicate_user(client: AsyncClient, sample_user_data: dict):
    """Test registering duplicate user returns 409."""
    # Register first user
    response1 = await client.post("/api/v1/auth/register", json=sample_user_data)
    assert response1.status_code == 201
    
    # Try to register same user again
    response2 = await client.post("/api/v1/auth/register", json=sample_user_data)
    assert response2.status_code == 409


@pytest.mark.integration
async def test_login_user(client: AsyncClient, sample_user_data: dict):
    """Test user login."""
    # Register user first
    await client.post("/api/v1/auth/register", json=sample_user_data)
    
    # Login
    login_data = {
        "email": sample_user_data["email"],
        "password": sample_user_data["password"]
    }
    response = await client.post("/api/v1/auth/login", json=login_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.integration
async def test_login_invalid_credentials(client: AsyncClient):
    """Test login with invalid credentials returns 401."""
    login_data = {
        "email": "nonexistent@example.com",
        "password": "WrongPassword123"
    }
    response = await client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 401


@pytest.mark.integration
async def test_refresh_token(client: AsyncClient, sample_user_data: dict):
    """Test token refresh."""
    # Register user
    response = await client.post("/api/v1/auth/register", json=sample_user_data)
    assert response.status_code == 201
    token_data = response.json()
    
    # Refresh token
    refresh_data = {"refresh_token": token_data["refresh_token"]}
    response = await client.post("/api/v1/auth/refresh", json=refresh_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
