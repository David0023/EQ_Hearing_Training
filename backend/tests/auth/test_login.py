import pytest
import asyncio

pytestmark = pytest.mark.anyio



async def test_login_returns_access_token(client, register_info):
    response = await client.post(
        "/auth/login",
        data={
            "username": register_info['email'],
            "password": register_info['password'],
        },
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]

async def test_login_sets_refresh_token(client, register_info):
    response = await client.post(
        "/auth/login",
        data={
            "username": register_info['email'],
            "password": register_info['password'],
        },
    )
    set_cookie = response.headers["set-cookie"].lower()
    assert "refresh_token=" in set_cookie
    assert "httponly" in set_cookie
    assert "secure" in set_cookie
    assert "samesite=lax" in set_cookie
    assert "path=/auth" in set_cookie

async def test_login_wrong_info_rejection(client, register_info):
    # Wrong email
    response = await client.post(
        "/auth/login",
        data={
            "username": 'wrong_' + register_info['email'],
            "password": register_info['password'],
        },
    )
    assert response.status_code == 401

    # Wrong password
    response = await client.post(
        "/auth/login",
        data={
            "username": register_info['email'],
            "password": 'wrong_' + register_info['password'],
        },
    )
    assert response.status_code == 401

async def test_different_token_after_refresh(client, register_info):
    res = await client.post(
        "/auth/login",
        data={
            "username": register_info['email'],
            "password": register_info['password'],
        },
    )

    assert res.status_code == 200
    refresh_token1 = res.cookies["refresh_token"]

    res = await client.post(
        "/auth/refresh",
        headers={"Cookie": f"refresh_token={refresh_token1}"},
    )
    assert res.status_code == 200

    # Check refresh success
    set_cookie = res.headers["set-cookie"].lower()
    assert "refresh_token=" in set_cookie
    assert "httponly" in set_cookie
    assert "secure" in set_cookie
    assert "samesite=lax" in set_cookie
    assert "path=/auth" in set_cookie

    refresh_token2 = res.cookies["refresh_token"]

    # Tokens must be different after refresh
    assert refresh_token1 != refresh_token2

async def test_refresh_with_invalid_token(client, register_info):
    response = await client.post(
        "/auth/login",
        data={
            "username": register_info['email'],
            "password": register_info['password'],
        },
    )

    refresh_token = response.cookies["refresh_token"]
    response = await client.post(
        "/auth/refresh", 
        headers={"Cookie": f"refresh_token={'wrong' + refresh_token}"},
    )

    assert response.status_code == 401