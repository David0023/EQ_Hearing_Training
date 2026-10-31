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

async def test_refresh_fails_after_user_deletion(authenticated_client, register_info):
    refresh_token = authenticated_client.cookies.get("refresh_token")

    # Delete user must succeed.
    response = await authenticated_client.request(
        "DELETE",
        '/api/v1/users/me',
        json={'password': register_info['password']}
    )
    assert response.status_code == 204

    # Refresh must fail after user deletion
    response = await authenticated_client.post(
        "/auth/refresh", 
        headers={"Cookie": f"refresh_token={refresh_token}"},
    )
    assert response.status_code == 401

async def test_access_token_invalidated_after_user_deletion(authenticated_client, register_info):
    access_token = authenticated_client.headers.get('Authorization', None)
    assert access_token is not None

    # Delete user must succeed.
    response = await authenticated_client.request(
        "DELETE",
        '/api/v1/users/me',
        json={'password': register_info['password']}
    )
    assert response.status_code == 204

    # Access should be denied after user deletion
    response = await authenticated_client.get(
        "/api/v1/users/me", 
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 401

async def test_refresh_fails_after_user_logout(authenticated_client):
    refresh_token = authenticated_client.cookies.get("refresh_token")

    response = await authenticated_client.post(
        "/auth/logout",
        headers={"Cookie": f"refresh_token={refresh_token}"},
    )
    assert response.status_code == 204

    # Refresh must fail after user logout
    response = await authenticated_client.post(
        "/auth/refresh", 
        headers={"Cookie": f"refresh_token={refresh_token}"},
    )
    assert response.status_code == 401


async def test_refresh_race_conditions(authenticated_client):
    # Refresh race condition: Only one refresh should succeed, as it rotates token after.
    responses = await asyncio.gather(*[
        authenticated_client.post('/auth/refresh')
        for i in range(10)
    ])

    status_codes = {response.status_code for response in responses}
    status_counts = {
        code: sum(response.status_code == code for response in responses)
        for code in status_codes
    }
    assert status_counts == {200: 1, 401: 9}, [r.text for r in responses]