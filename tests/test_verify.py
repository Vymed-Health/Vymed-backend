"""
Tests for the verification API endpoint.
"""

import pytest
from httpx import AsyncClient, ASGITransport

from src.main import app


@pytest.fixture
def client():
    """Create test client."""
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.asyncio
async def test_verify_endpoint_success(client):
    """Test successful verification request."""
    response = await client.post(
        "/api/v1/verify",
        json={
            "unit_id": "GS1-TEST-001",
            "device_id": "test-device-001",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] in ["verified", "warning", "recalled", "counterfeit"]


@pytest.mark.asyncio
async def test_verify_endpoint_missing_fields(client):
    """Test verification with missing required fields."""
    response = await client.post(
        "/api/v1/verify",
        json={},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_health_endpoint(client):
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
