import pytest

pytestmark = pytest.mark.anyio

async def test_refresh_token_expire(authenticated_client):
    from datetime import datetime, timezone
    from db.database import SessionLocal
    from auth.refresh_token.repository import get_one
    from auth.refresh_token.model import RefreshToken
    from auth.security import hash_refresh_token
    async with SessionLocal() as db:
        refresh_token = await get_one(
            db, 
            RefreshToken.token_hash == hash_refresh_token(authenticated_client.cookies.get("refresh_token"))
        )
        assert refresh_token is not None
        refresh_token.expires_at = datetime.now(timezone.utc)
        await db.commit()

    res = await authenticated_client.post(
        "/auth/refresh",
    )
    assert res.status_code == 401

async def test_refresh_token_hashed_when_stored(authenticated_client):
    from db.database import SessionLocal
    from auth.refresh_token.repository import get_one
    from auth.refresh_token.model import RefreshToken
    from auth.security import hash_refresh_token
    async with SessionLocal() as db:
        refresh_token = await get_one(
            db, 
            RefreshToken.token_hash == authenticated_client.cookies.get("refresh_token")
        )
        assert refresh_token is None

        refresh_token = await get_one(
            db, 
            RefreshToken.token_hash == hash_refresh_token(authenticated_client.cookies.get("refresh_token"))
        )
        assert refresh_token is not None