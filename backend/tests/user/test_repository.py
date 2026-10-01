import pytest

from user import repository as user_repository

pytestmark = pytest.mark.anyio


async def test_user_creation_failure_rolls_back(client, headers):
    from db.database import SessionLocal
    async with SessionLocal() as db:
        with pytest.raises(user_repository.UserCreationException):
            await user_repository.create(db, 'tester@example.com', 'duplicate', 'hash')
        # The same session must be usable after the failed commit.
        created = await user_repository.create(db, 'fresh@example.com', 'fresh', 'hash')
        assert created.id is not None
