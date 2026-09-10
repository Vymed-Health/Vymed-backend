"""
Tests for Recall Management API routes (VH-B03).
"""

from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.asyncio
async def test_initiate_recall_success(client):
    """Test initiating a batch recall operation."""
    mock_recall_id = uuid4()
    mock_recall_result = {
        "recall_id": mock_recall_id,
        "asset_code": "AMOX500B01",
        "status": "initiated",
        "reason": "Stability testing failure in storage conditions.",
        "transaction_hash": "tx_clawback_hash_999",
    }

    with patch("src.api.v1.recalls.StellarService.execute_recall", new_callable=AsyncMock) as mock_recall:
        mock_recall.return_value = mock_recall_result

        response = await client.post(
            "/api/v1/recalls",
            json={
                "asset_code": "AMOX500B01",
                "reason": "Stability testing failure in storage conditions.",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["asset_code"] == "AMOX500B01"
        assert data["status"] == "initiated"
        assert data["reason"] == "Stability testing failure in storage conditions."


@pytest.mark.asyncio
async def test_initiate_recall_validation_error(client):
    """Test recall request with too short reason."""
    response = await client.post(
        "/api/v1/recalls",
        json={
            "asset_code": "AMOX500B01",
            "reason": "Short",  # < 10 characters minimum
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_recall_status_found(client):
    """Test querying status of an existing recall."""
    mock_recall_id = uuid4()
    mock_data = {
        "recall_id": mock_recall_id,
        "asset_code": "AMOX500B01",
        "status": "completed",
        "reason": "Severe adverse event cluster report",
        "transaction_hash": "tx_hash_done",
        "created_at": "2026-09-10T12:00:00Z",
    }

    with patch("src.api.v1.recalls.StellarService.get_recall_status", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_data

        response = await client.get(f"/api/v1/recalls/{mock_recall_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["asset_code"] == "AMOX500B01"


@pytest.mark.asyncio
async def test_get_recall_status_not_found(client):
    """Test querying non-existent recall."""
    random_id = uuid4()
    with patch("src.api.v1.recalls.StellarService.get_recall_status", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None

        response = await client.get(f"/api/v1/recalls/{random_id}")
        assert response.status_code == 404
