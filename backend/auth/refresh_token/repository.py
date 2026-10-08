from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from auth.refresh_token.model import RefreshToken

async def get_one(
    db: AsyncSession,
    *conditions,
    lock: bool = False,
) -> RefreshToken | None:
    """Return the refresh token matching the supplied conditions."""
    query = select(RefreshToken).where(*conditions)
    if lock:
        query = query.with_for_update()
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def create(
    db: AsyncSession,
    user_id: int,
    token_hash: str,
    expires_at: datetime,
) -> RefreshToken:
    """Add and flush a refresh-token row."""
    new_token = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at
    )
    db.add(new_token)
    await db.flush()
    return new_token

async def revoke(
    db: AsyncSession,
    token: RefreshToken,
    revoked_at: datetime,
) -> RefreshToken:
    """Mark a refresh token as revoked in the current transaction."""
    token.revoked_at = revoked_at
    return token
