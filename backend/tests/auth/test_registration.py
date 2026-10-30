import pytest
import asyncio
pytestmark = pytest.mark.anyio


async def test_register_returns_user(client):
    res = await client.post(
        '/auth/register',
        json={
            'username': 'test',
            'email': 'test@example.com',
            'password': 'test-password',
        },
    )

    assert res.status_code == 201
    body = res.json()
    assert body['username'] == 'test'
    assert body['email'] == 'test@example.com'
    assert 'password' not in body
    assert 'hashed_pwd' not in body

async def test_register_duplicate_email(client, register_info):
    res = await client.post(
        '/auth/register',
        json={
            'username': 'username',
            'email': register_info['email'],
            'password': 'test-password',
        },
    )
    assert res.status_code == 409

async def test_register_invalid_inputs(client):
    # Invalid username character
    res = await client.post(
        '/auth/register',
        json={
            'username': 'inv@alid',
            'email': 'test@example.com',
            'password': 'test-password',
        },
    )
    assert res.status_code == 422

    # too short/long username
    res = await client.post(
        '/auth/register',
        json={
            'username': 'a',
            'email': 'test@example.com',
            'password': 'test-password',
        },
    )
    assert res.status_code == 422
    res = await client.post(
        '/auth/register',
        json={
            'username': 'thisistoolongtobeusedforausername',
            'email': 'test@example.com',
            'password': 'test-password',
        },
    )
    assert res.status_code == 422

    # too short password
    res = await client.post(
        '/auth/register',
        json={
            'username': 'valid',
            'email': 'test@example.com',
            'password': 'tooshort',
        },
    )

    # Invalid email format
    assert res.status_code == 422
    res = await client.post(
        '/auth/register',
        json={
            'username': 'valid',
            'email': 'testexample.com',
            'password': 'test-password',
        },
    )
    assert res.status_code == 422
    res = await client.post(
        '/auth/register',
        json={
            'username': 'valid',
            'email': 'test@ex@ample.com',
            'password': 'test-password',
        },
    )
    assert res.status_code == 422


async def test_register_duplicate_username(client, register_info):
    res = await client.post(
        '/auth/register',
        json={
            'username': register_info['username'],
            'email': 'different@example.com',
            'password': 'test-password',
        },
    )
    assert res.status_code == 201


async def test_race_register(client):
    # Race - Unique email registration at once
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