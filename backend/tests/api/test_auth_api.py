import asyncio
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select

from auth import security
from auth.refresh_token.model import RefreshToken
from db import database
from training.session import repository as session_repository
from tests.training.helpers import BASE, create_session

pytestmark = pytest.mark.anyio


async def test_auth_and_account_deletion(client, headers):
    assert (await client.get('/api/v1/users/me')).status_code == 401
    response = await client.get('/api/v1/users/me', headers=headers)
    assert response.json()['email'] == 'tester@example.com'
    assert 'hashed_pwd' not in response.json()
    response = await client.post('/auth/login', data={
        'username': 'tester@example.com', 'password': 'wrong',
    })
    assert response.status_code == 401
    duplicate = await client.post('/auth/register', json={
        'username': 'tester', 'email': 'tester@example.com', 'password': 'test-password',
    })
    assert duplicate.status_code == 409 
    sid = await create_session(client, headers)
    assert (await client.post(f'{BASE}/sessions/{sid}/questions', headers=headers)).status_code == 201
    response = await client.request(
        'DELETE',
        '/api/v1/users/me',
        headers=headers,
        json={'password': 'test-password'},
    )
    assert response.status_code == 204 and not response.content
    assert (await client.get('/api/v1/users/me', headers=headers)).status_code == 401
    async with database.SessionLocal() as db:
        assert await session_repository.get_many(db) == []


async def test_account_deletion_requires_correct_password(client, headers):
    response = await client.request(
        'DELETE', '/api/v1/users/me', headers=headers,
        json={'password': 'incorrect-password'},
    )
    assert response.status_code == 401, response.text

    # A rejected deletion must leave the account and its token usable.
    profile = await client.get('/api/v1/users/me', headers=headers)
    assert profile.status_code == 200, profile.text


async def register_and_login(client, email='tester@example.com', username='tester'):
    """Create a user and return the complete login token pair."""
    response = await client.post('/auth/register', json={
        'username': username, 'email': email, 'password': 'test-password',
    })
    assert response.status_code == 201, response.text
    response = await client.post('/auth/login', data={
        'username': email, 'password': 'test-password',
    })
    assert response.status_code == 200, response.text
    return response.json()


async def test_login_issues_distinct_refresh_tokens_without_caching(client):
    """Each login creates an independent, non-cacheable refresh credential."""
    first = await register_and_login(client)
    second = (await client.post('/auth/login', data={
        'username': 'tester@example.com', 'password': 'test-password',
    }))

    assert second.status_code == 200, second.text
    assert first['refresh_token'] != second.json()['refresh_token']
    assert second.headers['cache-control'] == 'no-store'
    assert second.headers['pragma'] == 'no-cache'


async def test_refresh_rotates_token_and_rejects_previous_token(client):
    """A successful refresh returns a fresh pair and consumes the old refresh token."""
    tokens = await register_and_login(client)

    response = await client.post('/auth/refresh', json={
        'refresh_token': tokens['refresh_token'],
    })

    assert response.status_code == 200, response.text
    rotated = response.json()
    assert rotated['refresh_token'] != tokens['refresh_token']
    assert response.headers['cache-control'] == 'no-store'
    assert response.headers['pragma'] == 'no-cache'
    replay = await client.post('/auth/refresh', json={
        'refresh_token': tokens['refresh_token'],
    })
    assert replay.status_code == 401


async def test_refresh_tokens_are_stored_as_hashes(client, db_session):
    """The database keeps only the hash, never the bearer secret."""
    tokens = await register_and_login(client)
    stored = await db_session.scalar(select(RefreshToken))

    assert stored is not None
    assert stored.token_hash == security.hash_refresh_token(tokens['refresh_token'])
    assert stored.token_hash != tokens['refresh_token']


async def test_expired_and_unknown_refresh_tokens_are_rejected(client, db_session):
    """Expired and unrecognized credentials both fail as unauthorized."""
    tokens = await register_and_login(client)
    stored = await db_session.scalar(select(RefreshToken))
    stored.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    await db_session.commit()

    expired = await client.post('/auth/refresh', json={
        'refresh_token': tokens['refresh_token'],
    })
    unknown = await client.post('/auth/refresh', json={'refresh_token': 'not-a-token'})

    assert expired.status_code == 401
    assert unknown.status_code == 401


async def test_logout_revokes_owned_refresh_token(client):
    """Logout revokes the supplied token and prevents a later refresh."""
    tokens = await register_and_login(client)
    headers = {'Authorization': f"Bearer {tokens['access_token']}"}

    response = await client.post('/auth/logout', headers=headers, json={
        'refresh_token': tokens['refresh_token'],
    })

    assert response.status_code == 204
    refresh = await client.post('/auth/refresh', json={
        'refresh_token': tokens['refresh_token'],
    })
    assert refresh.status_code == 401


async def test_logout_cannot_revoke_another_users_refresh_token(client):
    """Logout checks token ownership before revoking a session."""
    first = await register_and_login(client)
    second = await register_and_login(
        client, email='other@example.com', username='other',
    )
    headers = {'Authorization': f"Bearer {first['access_token']}"}

    response = await client.post('/auth/logout', headers=headers, json={
        'refresh_token': second['refresh_token'],
    })
    assert response.status_code == 401

    still_valid = await client.post('/auth/refresh', json={
        'refresh_token': second['refresh_token'],
    })
    assert still_valid.status_code == 200


async def test_user_deletion_invalidates_access_and_refresh_tokens(client):
    """Deleting an account removes its refresh credentials and invalidates access."""
    tokens = await register_and_login(client)
    headers = {'Authorization': f"Bearer {tokens['access_token']}"}

    deleted = await client.request(
        'DELETE', '/api/v1/users/me', headers=headers,
        json={'password': 'test-password'},
    )

    assert deleted.status_code == 204
    assert (await client.get('/api/v1/users/me', headers=headers)).status_code == 401
    assert (await client.post('/auth/refresh', json={
        'refresh_token': tokens['refresh_token'],
    })).status_code == 401


async def test_concurrent_refresh_allows_only_one_rotation(client):
    """PostgreSQL row locking lets exactly one request consume a refresh token."""
    tokens = await register_and_login(client)
    payload = {'refresh_token': tokens['refresh_token']}

    first, second = await asyncio.gather(
        client.post('/auth/refresh', json=payload),
        client.post('/auth/refresh', json=payload),
    )

    assert sorted([first.status_code, second.status_code]) == [200, 401]
