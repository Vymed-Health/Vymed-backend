"""
Rate Limiter Service with Redis Token-Bucket Algorithm (VH-B06)

Provides:
- Redis-backed token bucket rate limiting with automatic in-memory fallback.
- Per-IP and per-token brute-force protection for `/api/v1/verify`.
- Unit/device scan throttling.
"""

import time
from typing import Dict, Optional, Tuple

import redis.asyncio as redis
from fastapi import HTTPException, Request, status

from src.core.config import settings


class RateLimiter:
    """
    Redis-based Token-Bucket Rate Limiter.
    Enforces capacity limits and refill rates to mitigate automated brute-force attacks.
    """

    def __init__(
        self,
        redis_url: Optional[str] = None,
        default_capacity: int = 10,
        refill_rate_per_sec: float = 0.2,  # 1 token every 5 seconds
    ):
        self.redis_url = redis_url or settings.REDIS_URL
        self.redis_client = None
        self.default_capacity = default_capacity
        self.refill_rate = refill_rate_per_sec
        self.max_scans = settings.RATE_LIMIT_MAX_SCANS
        self.window_seconds = settings.RATE_LIMIT_WINDOW_SECONDS

        # In-memory fallback bucket store: key -> {"tokens": float, "last_updated": float}
        self._memory_buckets: Dict[str, Dict[str, float]] = {}
        self._memory_counts: Dict[str, int] = {}

    async def _get_redis(self) -> Optional[redis.Redis]:
        """Lazy-initialize Redis connection with fallback handling."""
        if self.redis_client is None:
            try:
                client = redis.from_url(
                    self.redis_url,
                    decode_responses=True,
                )
                await client.ping()
                self.redis_client = client
            except Exception:
                self.redis_client = None
        return self.redis_client

    async def consume_token(
        self,
        key: str,
        cost: float = 1.0,
        capacity: Optional[int] = None,
        refill_rate: Optional[float] = None,
    ) -> Tuple[bool, float]:
        """
        Token-bucket consumption algorithm.

        Args:
            key: Unique bucket identifier (e.g., 'ip:192.168.1.1' or 'verify:token').
            cost: Tokens required for this operation.
            capacity: Max bucket capacity.
            refill_rate: Tokens added per second.

        Returns:
            Tuple of (allowed: bool, remaining_tokens: float).
        """
        cap = float(capacity or self.default_capacity)
        rate = float(refill_rate or self.refill_rate)
        now = time.time()

        client = await self._get_redis()

        if client is not None:
            try:
                # Redis token bucket via hash
                bucket_key = f"tb:{key}"
                data = await client.hgetall(bucket_key)
                if data and "tokens" in data and "last_updated" in data:
                    tokens = float(data["tokens"])
                    last_updated = float(data["last_updated"])
                    elapsed = max(0.0, now - last_updated)
                    tokens = min(cap, tokens + elapsed * rate)
                else:
                    tokens = cap

                if tokens >= cost:
                    tokens -= cost
                    await client.hset(bucket_key, mapping={"tokens": str(tokens), "last_updated": str(now)})
                    await client.expire(bucket_key, int(cap / rate) + 60)
                    return True, tokens
                else:
                    await client.hset(bucket_key, mapping={"tokens": str(tokens), "last_updated": str(now)})
                    return False, tokens
            except Exception:
                # Fall back to in-memory logic
                pass

        # In-memory Token Bucket fallback
        bucket = self._memory_buckets.get(key)
        if bucket is not None:
            tokens = bucket["tokens"]
            last_updated = bucket["last_updated"]
            elapsed = max(0.0, now - last_updated)
            tokens = min(cap, tokens + elapsed * rate)
        else:
            tokens = cap

        if tokens >= cost:
            tokens -= cost
            self._memory_buckets[key] = {"tokens": tokens, "last_updated": now}
            return True, tokens
        else:
            self._memory_buckets[key] = {"tokens": tokens, "last_updated": now}
            return False, tokens

    async def check_rate_limit(
        self,
        unit_id: str,
        device_id: str,
    ) -> Tuple[bool, int]:
        """
        Check unit scan rate limit.
        """
        client = await self._get_redis()
        key = f"throttle:{unit_id}:{device_id}"

        if client is not None:
            try:
                scan_count = await client.get(key)
                count = int(scan_count) if scan_count else 0
                return (count >= self.max_scans), count
            except Exception:
                pass

        count = self._memory_counts.get(key, 0)
        return (count >= self.max_scans), count

    async def increment_scan_count(
        self,
        unit_id: str,
        device_id: str,
    ) -> int:
        """
        Increment unit scan count.
        """
        client = await self._get_redis()
        key = f"throttle:{unit_id}:{device_id}"

        if client is not None:
            try:
                scan_count = await client.incr(key)
                if scan_count == 1:
                    await client.expire(key, self.window_seconds)
                return scan_count
            except Exception:
                pass

        count = self._memory_counts.get(key, 0) + 1
        self._memory_counts[key] = count
        return count

    async def reset_scan_count(
        self,
        unit_id: str,
        device_id: str,
    ) -> None:
        """
        Reset unit scan count.
        """
        client = await self._get_redis()
        key = f"throttle:{unit_id}:{device_id}"

        if client is not None:
            try:
                await client.delete(key)
            except Exception:
                pass

        self._memory_counts.pop(key, None)

    async def close(self) -> None:
        """Close the Redis connection."""
        if self.redis_client:
            try:
                await self.redis_client.close()
            except Exception:
                pass
            self.redis_client = None


# Global rate limiter instance for API dependencies
global_rate_limiter = RateLimiter()


async def verify_rate_limit_dependency(request: Request):
    """
    FastAPI dependency enforcing Token-Bucket rate limiting on verification endpoints (VH-B06).
    Limits clients by IP address to prevent brute-force attacks.
    """
    client_ip = request.client.host if request.client else "127.0.0.1"
    bucket_key = f"ip:{client_ip}"

    allowed, remaining = await global_rate_limiter.consume_token(
        key=bucket_key,
        cost=1.0,
        capacity=10,
        refill_rate=0.5,
    )

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many verification requests. Token bucket exhausted. Please wait before retrying.",
            headers={"Retry-After": "5"},
        )
