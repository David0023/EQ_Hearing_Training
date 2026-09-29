from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import AsyncGenerator

from core.config import settings
from db.base import Base
from db import models  # Register every model independently of router imports.


# SQL Alchemy engine for postgresql
engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True, future=True)

# Class for creating new sessions
SessionLocal = async_sessionmaker(engine, autocommit=False, autoflush=False, expire_on_commit=False)

async def init_db():
    """Create the database tables defined by the metadata."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield a database session and close it after use."""
    async with SessionLocal() as db:
        yield db
