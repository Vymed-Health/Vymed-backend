"""
Tests for the Redis-based rate limiter service.
"""

import pytest

from src.services.rate_limiter import RateLimiter


@pytest.mark.asyncio
async def test_rate_limiter_first_scan():
    """Test that first scan is not rate limited."""
    limiter = RateLimiter()
    is_throttled, count = await limiter.check_rate_limit(
        unit_id="TEST-UNIT-001",
        device_id="TEST-DEVICE-001",
    )
    assert not is_throttled
    assert count == 0


@pytest.mark.asyncio
async def test_rate_limiter_increment():
    """Test incrementing scan count."""
    limiter = RateLimiter()
    await limiter.reset_scan_count(
        unit_id="TEST-UNIT-002",
        device_id="TEST-DEVICE-002",
    )

    count = await limiter.increment_scan_count(
        unit_id="TEST-UNIT-002",
        device_id="TEST-DEVICE-002",
    )
    assert count == 1


@pytest.mark.asyncio
async def test_rate_limiter_threshold():
    """Test that rate limiter triggers after max scans."""
    limiter = RateLimiter()
    unit_id = "TEST-UNIT-003"
    device_id = "TEST-DEVICE-003"

    await limiter.reset_scan_count(unit_id, device_id)

    # Simulate max scans
    for _ in range(limiter.max_scans):
        await limiter.increment_scan_count(unit_id, device_id)

    # Next scan should be throttled
    is_throttled, count = await limiter.check_rate_limit(unit_id, device_id)
    assert is_throttled
    assert count >= limiter.max_scans
