from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from auth.refresh_token import repository
from auth.refresh_token.model import RefreshToken

class TokenDuplicate(Exception):
    pass

class TokenNotFound(Exception):
    pass

class TokenExpired(Exception):
    pass

class TokenRevoked(Exception):
    pass

def is_token_unique_violation(exc: IntegrityError) -> bool:
    original = exc.orig
    constraint_name = getattr(original, "constraint_name", None)

    if constraint_name is None:
        diag = getattr(original, "diag", None)
        constraint_name = getattr(diag, "constraint_name", None)

    if constraint_name == "uq_token_hash":
        return True

    # PostgreSQL drivers do not all expose constraint_name on the same object.
    # The server error message still includes the named constraint.
    original_message = str(original)
    return (
        '"uq_token_hash"' in original_message
        or "UNIQUE constraint failed: refresh_tokens.token_hash" in original_message
    )

async def create(
    db: AsyncSession,
    user_id: int,
    token_hash: str,
    expires_at: datetime,
) -> RefreshToken:
    try:
        token = await repository.create(db,
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        return token
    except IntegrityError as exc:
        if is_token_unique_violation(exc):
            raise TokenDuplicate()
        raise

async def get_valid(
    db: AsyncSession,
    token_hash: str,
    user_id: int | None = None,
) -> RefreshToken:
    conditions = [RefreshToken.token_hash == token_hash]
    if user_id is not None:
        conditions.append(RefreshToken.user_id == user_id)
    refresh_token = await repository.get_one(db, *conditions, lock=True)

    if not refresh_token:
        raise TokenNotFound()
    if refresh_token.revoked_at:
        raise TokenRevoked()
    expires_at = refresh_token.expires_at
    if expires_at.tzinfo is None:
        # SQLite drops timezone metadata for DateTime(timezone=True) values.
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at <= datetime.now(timezone.utc):
        raise TokenExpired()
    return refresh_token

async def revoke(db: AsyncSession, token: RefreshToken) -> RefreshToken:
    await repository.revoke(db, token, datetime.now(timezone.utc))
    return token
