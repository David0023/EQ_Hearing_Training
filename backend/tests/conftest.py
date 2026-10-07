import os
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


TEST_DATABASE_URL = os.environ.get('TEST_DATABASE_URL')
if not TEST_DATABASE_URL:
    raise pytest.UsageError(
        'TEST_DATABASE_URL is required. Point it at a dedicated PostgreSQL test database.'
    )

test_url = make_url(TEST_DATABASE_URL)
if test_url.drivername != 'postgresql+asyncpg':
    raise pytest.UsageError(
        'TEST_DATABASE_URL must use PostgreSQL with asyncpg '
        '(postgresql+asyncpg://...). SQLite is not supported by the test suite.'
    )
if not test_url.database or 'test' not in test_url.database.lower():
    raise pytest.UsageError(
        'TEST_DATABASE_URL must point to a dedicated database whose name includes "test".'
    )

# Ensure application settings never fall back to a developer database.
os.environ['SECRET_KEY'] = 'test-secret-key-for-feature-refactor-only'
os.environ['DATABASE_URL'] = TEST_DATABASE_URL

from db import database
from main import app


@pytest.fixture
def anyio_backend():
    return 'asyncio'


@pytest.fixture
async def client(monkeypatch):
    """Use a fresh PostgreSQL schema per test to isolate rows and support row locks."""
    schema = f'pytest_{uuid4().hex}'
    admin_engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={'timeout': 10},
    )
    async with admin_engine.begin() as connection:
        await connection.execute(text(f'CREATE SCHEMA "{schema}"'))

    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={
            'timeout': 10,
            'server_settings': {'search_path': schema},
        },
    )
    monkeypatch.setattr(database, 'engine', engine)
    monkeypatch.setattr(
        database,
        'SessionLocal',
        async_sessionmaker(engine, expire_on_commit=False),
    )
    # Email deliverability uses external DNS; keep the API and database path real.
    monkeypatch.setattr('auth.service.check_email', lambda email: (True, email.lower()))

    try:
        async with app.router.lifespan_context(app):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url='http://test'
            ) as test_client:
                yield test_client
    finally:
        await engine.dispose()
        async with admin_engine.begin() as connection:
            await connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        await admin_engine.dispose()


@pytest.fixture
async def headers(client):
    response = await client.post('/auth/register', json={
        'username': 'tester', 'email': 'tester@example.com', 'password': 'test-password',
    })
    assert response.status_code == 201, response.text
    response = await client.post('/auth/login', data={
        'username': 'tester@example.com', 'password': 'test-password',
    })
    assert response.status_code == 200, response.text
    return {'Authorization': f'Bearer {response.json()["access_token"]}'}


@pytest.fixture
async def db_session(client):
    from db.database import SessionLocal

    async with SessionLocal() as db:
        yield db
