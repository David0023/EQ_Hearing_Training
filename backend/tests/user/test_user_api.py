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

    status_codes = {response.status_code for response in responses}
    status_counts = {
        code: sum(response.status_code == code for response in responses)
        for code in status_codes
    }
    assert status_counts == {201: 1, 409: 9}, [r.text for r in responses]
