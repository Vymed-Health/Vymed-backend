"""
Tests for Batch Management API routes (VH-B03).
"""

from datetime import date
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
async def test_create_batch_success(client):
    """Test successful batch registration on the Stellar blockchain."""
    mock_batch_id = uuid4()
    mock_batch_data = {
        "batch_id": mock_batch_id,
        "asset_code": "AMOX500B01",
        "manufacturer_name": "Novartis Global",
        "total_units": 10000,
        "expiry_date": date(2028, 12, 31),
        "transaction_hash": "tx_mock_hash_12345",
        "created_at": "2026-09-10T12:00:00Z",
        "status": "active",
    }

    with patch("src.api.v1.batches.BatchService.create_batch", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_batch_data

        response = await client.post(
            "/api/v1/batches",
            json={
                "asset_code": "AMOX500B01",
                "manufacturer_name": "Novartis Global",
                "total_units": 10000,
                "expiry_date": "2028-12-31",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["asset_code"] == "AMOX500B01"
        assert data["manufacturer_name"] == "Novartis Global"
        assert data["total_units"] == 10000


@pytest.mark.asyncio
async def test_create_batch_validation_error(client):
    """Test batch creation failure on invalid asset code format."""
    response = await client.post(
        "/api/v1/batches",
        json={
            "asset_code": "lowercase_not_allowed",
            "manufacturer_name": "Novartis",
            "total_units": 100,
            "expiry_date": "2028-12-31",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_batch_found(client):
    """Test retrieving existing batch details."""
    mock_id = uuid4()
    mock_batch_data = {
        "batch_id": mock_id,
        "asset_code": "CIPRO500B02",
        "manufacturer_name": "Bayer AG",
        "total_units": 5000,
        "expiry_date": date(2027, 6, 30),
        "transaction_hash": "tx_mock_hash_67890",
        "created_at": "2026-09-10T12:00:00Z",
        "status": "active",
    }

    with patch("src.api.v1.batches.BatchService.get_batch", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_batch_data

        response = await client.get(f"/api/v1/batches/{mock_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["asset_code"] == "CIPRO500B02"


@pytest.mark.asyncio
async def test_get_batch_not_found(client):
    """Test retrieving non-existent batch."""
    random_id = uuid4()
    with patch("src.api.v1.batches.BatchService.get_batch", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None

        response = await client.get(f"/api/v1/batches/{random_id}")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_map_parent_child(client):
    """Test parent-child relationship mapping."""
    batch_id = uuid4()
    mock_map_result = {
        "batch_id": str(batch_id),
        "parent_id": "CARTON-001",
        "child_count": 2,
        "status": "mapped",
    }

    with patch("src.api.v1.batches.BatchService.map_parent_child", new_callable=AsyncMock) as mock_map:
        mock_map.return_value = mock_map_result

        response = await client.post(
            f"/api/v1/batches/{batch_id}/map",
            json={
                "parent_id": "CARTON-001",
                "child_ids": ["BOTTLE-01", "BOTTLE-02"],
            },
        )
        assert response.status_code == 200
        assert response.json()["status"] == "mapped"
