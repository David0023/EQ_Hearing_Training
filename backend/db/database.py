from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import AsyncGenerator

from core.config import settings


# SQL Alchemy engine for postgresql
engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True, future=True)

# Class for creating new sessions
SessionLocal = async_sessionmaker(engine, autocommit=False, autoflush=False, expire_on_commit=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield a database session and close it after use."""
    async with SessionLocal() as db:
        yield db
