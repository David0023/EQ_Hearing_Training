import pytest

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
