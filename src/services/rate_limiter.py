"""
Rate Limiter Service

Redis-based scan throttling to prevent scan-spamming attacks.
Limits verification scans to a configurable maximum per time window.
"""

from typing import Tuple

import redis.asyncio as redis

from src.core.config import settings


class RateLimiter:
    """
    Redis-based rate limiter for medication verification scans.

    Prevents "scan-spamming" where a single bottle is scanned repeatedly
    to spoof data or scrape supply chain intelligence.

    Threshold: Max 3 scans per 10 minutes for a single unique bottle.
    """

    def __init__(self):
        """Initialize Redis connection."""
        self.redis_client = None
        self.max_scans = settings.RATE_LIMIT_MAX_SCANS
        self.window_seconds = settings.RATE_LIMIT_WINDOW_SECONDS

    async def _get_redis(self) -> redis.Redis:
        """Lazy-initialize Redis connection."""
        if self.redis_client is None:
            self.redis_client = await redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
            )
        return self.redis_client

    async def check_rate_limit(
        self,
        unit_id: str,
        device_id: str,
    ) -> Tuple[bool, int]:
        """
        Check if a scan request is rate-limited.

        Args:
            unit_id: The GS1 DataMatrix Unit ID.
            device_id: The unique device identifier.

        Returns:
            Tuple of (is_throttled, current_scan_count).
        """
        client = await self._get_redis()
        key = f"throttle:{unit_id}:{device_id}"

        # Get current scan count
        scan_count = await client.get(key)
        scan_count = int(scan_count) if scan_count else 0

        # Check if threshold exceeded
        if scan_count >= self.max_scans:
            return True, scan_count

        return False, scan_count

    async def increment_scan_count(
        self,
        unit_id: str,
        device_id: str,
    ) -> int:
        """
        Increment the scan count for a unit-device combination.

        Args:
            unit_id: The GS1 DataMatrix Unit ID.
            device_id: The unique device identifier.

        Returns:
            The new scan count.
        """
        client = await self._get_redis()
        key = f"throttle:{unit_id}:{device_id}"

        # Increment and set TTL on first creation
        scan_count = await client.incr(key)

        if scan_count == 1:
            await client.expire(key, self.window_seconds)

        return scan_count

    async def reset_scan_count(
        self,
        unit_id: str,
        device_id: str,
    ) -> None:
        """
        Reset the scan count for a unit-device combination.

        Args:
            unit_id: The GS1 DataMatrix Unit ID.
            device_id: The unique device identifier.
        """
        client = await self._get_redis()
        key = f"throttle:{unit_id}:{device_id}"
        await client.delete(key)

    async def close(self) -> None:
        """Close the Redis connection."""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None
