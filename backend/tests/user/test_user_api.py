from unittest.mock import AsyncMock
import asyncio
import pytest

pytestmark = pytest.mark.anyio

async def test_user_creation(client):
    # Race condition - Unique
    responses = await asyncio.gather(*[
            client.post('/auth/register', json={
                'username': 'test_user',
                'email': f'race-test{i}@email.com',
                'password': 'test_password',
            })
            for i in range(10)
        ])
    for response in responses:
        assert response.status_code == 201

    # Race condition - Duplicate
    responses = await asyncio.gather(*[
        client.post('/auth/register', json={
            'username': 'test_user',
            'email': 'race-test_dup@email.com',
            'password': 'test_password',
        })
        for _ in range(10)
    ])

    codes = {}
    for response in responses:
        code = response.status_code
        codes[code] = 1 if code not in codes else codes[code] + 1
    assert codes.get(409, None), codes.get(409, None) == 9
    assert codes.get(201, None), codes.get(201, None) == 1