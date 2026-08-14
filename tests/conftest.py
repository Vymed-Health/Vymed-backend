"""
Shared test configuration.

Unit CI does not provision external services (Redis, Stellar credentials),
so tests that depend on them are skipped unless the corresponding
environment variables are set. This keeps the default ``pytest`` run green
without external dependencies while still executing the tests when the
full environment is available (set MANUFACTURER_SECRET_KEY / REDIS_URL).
"""

import os

import pytest


def pytest_collection_modifyitems(items):
    for item in items:
        module = item.getparent(pytest.Module)
        name = module.name if module is not None else ""

        if name == "test_stellar_service.py" and not os.getenv("MANUFACTURER_SECRET_KEY"):
            item.add_marker(
                pytest.mark.skip(
                    reason="MANUFACTURER_SECRET_KEY not set — Stellar-dependent tests skipped"
                )
            )

        if name == "test_rate_limiter.py" and not os.getenv("REDIS_URL"):
            item.add_marker(
                pytest.mark.skip(reason="REDIS_URL not set — Redis-dependent tests skipped")
            )

        if name == "test_verify.py" and not os.getenv("REDIS_URL"):
            test_name = getattr(item, "name", "")
            if test_name != "test_health_endpoint":
                item.add_marker(
                    pytest.mark.skip(
                        reason="REDIS_URL not set — verification endpoint tests skipped"
                    )
                )
