from contextlib import asynccontextmanager
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from auth import service
from auth.refresh_token import service as refresh_service
from user.schema import UserCreateRequest


class Database:
    def __init__(self):
        self.commit = AsyncMock()
        self.rollback = AsyncMock()

    @asynccontextmanager
    async def begin(self):
        yield

    @asynccontextmanager
    async def begin_nested(self):
        yield


def _user_request():
    return UserCreateRequest(username="tester", email="test@example.com", password="long-password-123")


@pytest.mark.anyio
async def test_register_validates_duplicate_and_persists(monkeypatch):
    db = Database()
    monkeypatch.setattr(service, "check_email", lambda value: (True, value.lower()))
    monkeypatch.setattr(service, "check_username", lambda value: (True, value.strip()))
    monkeypatch.setattr(service, "check_password", lambda value: (True, value))
    monkeypatch.setattr(service.user_repo, "get_one", AsyncMock(return_value=None))
    monkeypatch.setattr(service.user_repo, "create", AsyncMock(return_value="new-user"))
    monkeypatch.setattr(service.security, "hash_password", lambda value: f"hashed:{value}")
    assert await service.register(db, _user_request()) == "new-user"
    db.commit.assert_awaited_once()

    monkeypatch.setattr(service.user_repo, "get_one", AsyncMock(return_value=object()))
    with pytest.raises(service.DuplicateEmail):
        await service.register(db, _user_request())

    monkeypatch.setattr(service, "check_username", lambda value: (False, "invalid"))
    with pytest.raises(service.RegistrationBadInputException, match="Invalid Username"):
        await service.register(db, _user_request())


@pytest.mark.anyio
async def test_login_rejects_bad_credentials_and_returns_tokens(monkeypatch):
    db = Database()
    user = SimpleNamespace(id=7, hashed_pwd="stored")
    monkeypatch.setattr(service.user_repo, "get_one", AsyncMock(return_value=user))
    monkeypatch.setattr(service.security, "verify_password", lambda plain, hashed: plain == "good")
    monkeypatch.setattr(service.security, "create_access_token", lambda user_id, role: f"access-{user_id}-{role}")
    refresh = SimpleNamespace(raw_token="refresh")
    monkeypatch.setattr(service, "_store_refresh_token_with_retry", AsyncMock(return_value=refresh))

    with pytest.raises(service.InvalidLoginInfo):
        await service.login(db, "test@example.com", "bad")
    tokens = await service.login(db, "test@example.com", "good")
    assert tokens.access_token == "access-7-user"
    assert tokens.refresh_token is refresh


@pytest.mark.anyio
async def test_refresh_and_revoke_invalid_token_translation(monkeypatch):
    db = Database()
    monkeypatch.setattr(service.security, "hash_refresh_token", lambda raw: f"hash:{raw}")
    monkeypatch.setattr(refresh_service, "get_valid", AsyncMock(side_effect=refresh_service.TokenNotFound()))
    with pytest.raises(service.InvalidRefreshToken):
        await service.refresh(db, "missing")
    with pytest.raises(service.InvalidRefreshToken):
        await service.revoke_refresh_token(db, "missing", 1)
    assert db.rollback.await_count == 2

    old = SimpleNamespace(user_id=9)
    new = SimpleNamespace(raw_token="new")
    monkeypatch.setattr(refresh_service, "get_valid", AsyncMock(return_value=old))
    monkeypatch.setattr(service.security, "create_access_token", lambda user_id, role: "access")
    monkeypatch.setattr(service, "_store_refresh_token_with_retry", AsyncMock(return_value=new))
    monkeypatch.setattr(refresh_service, "revoke", AsyncMock())
    tokens = await service.refresh(db, "old")
    assert tokens.access_token == "access"
    assert tokens.refresh_token is new
    db.commit.assert_awaited_once()
