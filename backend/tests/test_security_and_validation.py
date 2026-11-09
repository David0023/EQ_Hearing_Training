from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi import HTTPException

from auth import security
from user.validators import check_password, check_username


def test_access_token_round_trip_and_invalid_tokens():
    token = security.create_access_token(42, "user")
    data = security.decode_token(token)
    assert (data.sub, data.role) == ("42", "user")

    with pytest.raises(HTTPException) as error:
        security.decode_token("not-a-token")
    assert error.value.status_code == 401

    expired = jwt.encode(
        {"sub": "42", "role": "user", "exp": datetime.now(timezone.utc) - timedelta(minutes=1), "iat": datetime.now(timezone.utc)},
        security.settings.SECRET_KEY,
        algorithm=security.settings.ALGORITHM,
    )
    with pytest.raises(HTTPException) as error:
        security.decode_token(expired)
    assert error.value.detail == "Token has expired"


def test_refresh_token_hashing_and_password_hashing():
    refresh = security.generate_refresh_token()
    assert refresh.raw_token
    assert security.hash_refresh_token(refresh.raw_token) == refresh.token_hash
    assert refresh.expires_at > refresh.created_at

    hashed = security.hash_password("correct horse battery staple")
    assert hashed != "correct horse battery staple"
    assert security.verify_password("correct horse battery staple", hashed)
    assert not security.verify_password("wrong password", hashed)


def test_username_and_password_validation_boundaries():
    assert check_username("  user_1  ") == (True, "user_1")
    assert check_username("ab")[0] is False
    assert check_username("user!")[0] is False
    assert check_password("a" * 12) == (True, "a" * 12)
    assert check_password("short")[0] is False
    assert check_password("a" * 129)[0] is False
