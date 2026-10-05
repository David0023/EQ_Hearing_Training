import os

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

# Always use an isolated test configuration, never a developer's database.
os.environ['SECRET_KEY'] = 'test-secret-key-for-feature-refactor-only'
os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///:memory:'

from db import database
from main import app


@pytest.fixture
def anyio_backend():
    return 'asyncio'


@pytest.fixture
async def client(tmp_path, monkeypatch):
    engine = create_async_engine(f'sqlite+aiosqlite:///{tmp_path / "test.db"}')

    @event.listens_for(engine.sync_engine, 'connect')
    def enable_foreign_keys(connection, _):
        connection.execute('PRAGMA foreign_keys=ON')

    monkeypatch.setattr(database, 'engine', engine)
    monkeypatch.setattr(database, 'SessionLocal', async_sessionmaker(engine, expire_on_commit=False))
    # Domain deliverability is an external DNS dependency; keep the API/DB path real.
    monkeypatch.setattr('auth.service.check_email', lambda email: (True, email.lower()))
    try:
        async with app.router.lifespan_context(app):
            async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
                yield client
    finally:
        await engine.dispose()


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
