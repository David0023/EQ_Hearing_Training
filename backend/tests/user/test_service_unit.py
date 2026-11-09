from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from user import service
from user.schema import UserSelfAuthenticationRequest


@pytest.mark.anyio
async def test_user_service_profile_and_deletion(monkeypatch):
    user = SimpleNamespace(id=5, hashed_pwd="saved")
    db = SimpleNamespace(commit=AsyncMock(), rollback=AsyncMock())
    monkeypatch.setattr(service.repository, "delete_this", AsyncMock())
    monkeypatch.setattr(service, "verify_password", lambda plain, hashed: True)
    await service.delete_user(UserSelfAuthenticationRequest(password="password"), db, user)
    db.commit.assert_awaited_once()


@pytest.mark.anyio
async def test_user_service_password_errors(monkeypatch):
    user = SimpleNamespace(hashed_pwd="saved")
    db = SimpleNamespace(commit=AsyncMock(), rollback=AsyncMock())
    monkeypatch.setattr(service, "verify_password", lambda plain, hashed: False)
    with pytest.raises(service.UserUnauthenticated):
        await service.delete_user(UserSelfAuthenticationRequest(password="bad"), db, user)
    db.rollback.assert_awaited_once()


@pytest.mark.anyio
async def test_profile_image_replacement_and_delete(monkeypatch, tmp_path):
    user = SimpleNamespace(profile_img_key="old.jpg")
    db = SimpleNamespace(commit=AsyncMock(), rollback=AsyncMock())
    monkeypatch.setattr(service.settings, "LOCAL_UPLOAD_DIR", tmp_path)
    monkeypatch.setattr(service.img_service, "upload_image", AsyncMock(return_value=SimpleNamespace(id="new", extension=".png")))
    monkeypatch.setattr(service.repository, "update", AsyncMock(return_value=user))
    result = await service.update_profile_image(db, user, object())
    assert result.profile_image_key == "new.png"
    assert result.obsolete_image_key == "old.jpg"
    db.commit.assert_awaited_once()

    deleted = await service.delete_profile_image(db, user)
    assert deleted == "old.jpg"
