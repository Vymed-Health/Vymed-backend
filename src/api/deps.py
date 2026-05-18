"""
API Dependencies

Shared dependency injection for API routes.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import async_session_factory


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide an async database session for route handlers.

    Yields:
        AsyncSession: Database session that auto-commits on success
        and rolls back on error.
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
