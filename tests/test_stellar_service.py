"""
Tests for the Stellar blockchain service.
"""

import pytest

from src.services.stellar_service import StellarService


@pytest.mark.asyncio
async def test_verify_unit_returns_dict():
    """Test that verify_unit returns a dictionary with expected keys."""
    service = StellarService()
    result = await service.verify_unit(unit_id="TEST-UNIT-001")

    assert isinstance(result, dict)
    assert "status" in result
    assert "message" in result


@pytest.mark.asyncio
async def test_mint_batch_asset_returns_dict():
    """Test that mint_batch_asset returns expected structure."""
    service = StellarService()
    result = await service.mint_batch_asset(
        asset_code="TEST001",
        amount=100,
    )

    assert isinstance(result, dict)
    assert result["asset_code"] == "TEST001"
    assert result["amount"] == 100


@pytest.mark.asyncio
async def test_execute_recall_returns_recall_id():
    """Test that execute_recall returns a recall ID."""
    service = StellarService()
    result = await service.execute_recall(
        asset_code="TEST001",
        reason="Quality control test failure",
    )

    assert isinstance(result, dict)
    assert "recall_id" in result
    assert result["status"] == "initiated"
