import os
from uuid import uuid4
import pytest
from httpx import ASGITransport, AsyncClient
from collections.abc import AsyncGenerator


from alembic import command
from alembic.config import Config
from asgi_lifespan import LifespanManager

from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession


# Whenever pytest.mark.anyio is used, it tells pytest to use this plugin
@pytest.fixture
def anyio_backend():
    return 'asyncio'

# Check Test database url settings
TEST_DATABASE_URL = os.environ.get('TEST_DATABASE_URL')
if not TEST_DATABASE_URL:
    raise pytest.UsageError(
        'TEST_DATABASE_URL is required. Point it at a dedicated PostgreSQL test database.'
    )

test_url = make_url(TEST_DATABASE_URL)
if test_url.drivername != 'postgresql+asyncpg':
    raise pytest.UsageError("TEST_DATABASE_URL must use PostgreSQL with asyncpg")
if not test_url.database or "test" not in test_url.database.lower():
    raise pytest.UsageError("TEST_DATABASE_URL must name a dedicated test database")


# This is required as main.app will use 'DATABASE_URL' when imported.
# Hence, we have to set its keys before import
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

from main import app
from db import database

@pytest.fixture
async def use_test_database(monkeypatch) -> AsyncGenerator[None, None]:
    admin_engine = None
    test_engine = None
    schema_created = False
    try:
        schema = f'pytest_{uuid4().hex}'

        # Admin engine to generate schema
        admin_engine = create_async_engine(TEST_DATABASE_URL)

        # Test engine for sessions and alembic
        test_engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={'server_settings': {'search_path': schema}})
        monkeypatch.setattr(database, 'engine', test_engine)

        TestSessionLocal = async_sessionmaker(
            test_engine,
            expire_on_commit=False
        )
        monkeypatch.setattr(database, 'SessionLocal', TestSessionLocal)

        alembic_config = Config(os.path.join(os.path.dirname(__file__), '..', 'alembic.ini'))
        def upgrade_schema(connection):
            alembic_config.attributes['connection'] = connection
            command.upgrade(alembic_config, 'head')

        async with admin_engine.begin() as connection:
            await connection.execute(text(f'CREATE SCHEMA "{schema}"'))
        schema_created = True

        async with test_engine.begin() as connection:
            await connection.run_sync(upgrade_schema)

        # Skip DNS check for test emails
        monkeypatch.setattr('auth.service.check_email', lambda email: (True, email.lower()))

        yield
    
    finally:
        if test_engine is not None:
            await test_engine.dispose()
        if admin_engine is not None:
            if schema_created:
                async with admin_engine.begin() as connection:
                    await connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
            await admin_engine.dispose()

@pytest.fixture
async def client(use_test_database) -> AsyncGenerator[AsyncClient, None]:
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(
            transport=transport,
            base_url='https://test'
        ) as test_client:
            yield test_client

@pytest.fixture
async def db_session(client) -> AsyncGenerator[AsyncSession, None]:
    from db.database import SessionLocal
    async with SessionLocal() as db:
        yield db

@pytest.fixture
async def register_info(client, monkeypatch) -> dict[str, str]:
    email = f"tester-{uuid4().hex}@example.com"
    username = f"tester-{uuid4().hex[:8]}"
    password = f"tester-{uuid4().hex[:8]}"
    response = await client.post(
        "/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password,
        },
    )
    assert response.status_code == 201, response.text

    return {"email": email, "username": username, "password": password}

@pytest.fixture
async def authenticated_client(client, register_info) -> AsyncGenerator[AsyncClient, None]:
    response = await client.post(
        "/auth/login",
        data={
            "username": register_info['email'],
            "password": register_info['password'],
        },
    )
    assert response.status_code == 200, response.text

    client.headers["Authorization"] = f"Bearer {response.json()['access_token']}"

    try:
        yield client
    finally:
        client.headers.pop("Authorization", None)
        client.cookies.delete("refresh_token")