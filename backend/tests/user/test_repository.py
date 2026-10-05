import pytest
from sqlalchemy.exc import IntegrityError

from user import repository as user_repository

pytestmark = pytest.mark.anyio


async def test_user_creation_repository(headers, db_session):
    # DB Constraint will raise Integrity Error for duplicate email.
    with pytest.raises(IntegrityError):
        await user_repository.create(
            db_session, 'tester@example.com', 'duplicate', 'hash', flush=True
        )

    await db_session.rollback()
    created = await user_repository.create(
        db_session, 'fresh@example.com', 'fresh', 'hash', flush=True
    )
    await db_session.commit()
    assert created.id is not None
