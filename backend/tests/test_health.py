"""Test health endpoint (Build Rule 7)."""
import pytest


@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


@pytest.mark.asyncio
async def test_health_no_auth_required(client):
    """Health check must not require authentication."""
    response = await client.get("/health")
    assert response.status_code == 200
